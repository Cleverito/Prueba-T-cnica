# Decisiones de diseño

Este documento explica el *por qué* detrás de las decisiones no obvias del proyecto. La mayoría de proyectos académicos muestran qué se hizo; este documento existe para mostrar qué alternativas se descartaron y por qué.

## 1. ¿Por qué SQL (PostgreSQL) y no NoSQL?

El dominio depende de relaciones con integridad referencial fuerte (candidato → partido, voto → candidato/partido) y de transacciones ACID — un voto no puede quedar registrado a medias. Las consultas más frecuentes (conteos, agregaciones por partido/candidato) son exactamente el caso de uso donde `JOIN` y `GROUP BY` superan a las bases NoSQL. NoSQL habría tenido sentido para escenarios de escritura masiva en tiempo real o esquemas altamente variables — ninguno de los dos aplica aquí.

## 2. ¿Por qué el voto puede ser a candidato o directo a partido?

Se decidió permitir ambas modalidades desde el inicio del diseño, reflejando sistemas electorales reales donde existe tanto el voto a un candidato como el voto en blanco/por lista. Esto llevó a que `Voto.candidato_id` sea opcional mientras que `Voto.partido_id` es siempre obligatorio — incluso cuando hay candidato, porque el partido es derivable y se necesita para las agregaciones de `/resultados`.

## 3. ¿Por qué la consistencia candidato↔partido se valida en el backend y no con un trigger en la base de datos?

La regla "si hay candidato, el partido del voto debe coincidir con el partido real de ese candidato" no es expresable con un `CHECK` constraint simple en SQL (un `CHECK` no puede hacer `JOIN` contra otra tabla). Las alternativas consideradas fueron:

1. Validar en el backend antes de insertar.
2. Un trigger en PostgreSQL como capa adicional.
3. Ambas (defensa en profundidad).

Se eligió la opción 1, en su forma más fuerte: en lugar de "validar y rechazar si no coincide", el backend **deriva** el `partido_id` directamente del candidato y nunca acepta ese valor del cliente cuando hay `candidato_id`. Esto elimina la inconsistencia por construcción, no solo la detecta. Se descartó el trigger porque el backend es el único punto de entrada a la base de datos en esta arquitectura (no hay clientes externos escribiendo directo a PostgreSQL), por lo que la capa adicional de un trigger añadía complejidad sin un beneficio proporcional para el alcance del proyecto.

## 4. ¿Por qué el voto es inmutable (sin `PUT`/`DELETE`)?

Permitir editar o borrar un voto ya registrado comprometería la integridad de cualquier proceso electoral: nadie debería poder alterar un voto después del hecho. Esta decisión rompe deliberadamente la simetría del CRUD genérico que sí aplica a `Partido` y `Candidato` — es una excepción consciente, no una omisión. La ausencia de estos endpoints está verificada por un test automatizado (`test_voto_no_tiene_endpoint_put`) que falla si alguien los agrega accidentalmente en el futuro.

## 5. ¿Por qué no existe relación entre `Voto` y `Votante`?

**Nota sobre el alcance**: el enunciado base de este proyecto exige únicamente vincular candidato, partido y momento del voto. El control de identidad del votante (verificación de cédula, bloqueo de doble voto) es una mejora añadida sobre ese enunciado, no un requisito explícito. Por eso, el parámetro `cedula` en `POST /votos` es opcional: si se omite, el voto se registra cumpliendo exactamente el enunciado base, sin pasar por ningún control de unicidad. Si se proporciona, se activa la mejora completa descrita a continuación.

Esta es la decisión central del diseño en torno al secreto del voto. El sistema necesita verificar que una cédula no vote dos veces, pero **no** necesita (ni debe) poder rastrear qué votó una cédula específica. La solución fue desacoplar completamente ambas tablas: `Votante` solo registra si una cédula ya votó (un estado), `Voto` solo registra qué se votó (sin ninguna referencia a quién). No existe ninguna clave foránea entre ambas, y esta ausencia es intencional, no un olvido — verificada también por un test (`test_listar_votos_no_expone_cedula`).

Se reconoce una limitación: la correlación temporal entre el registro del votante y la inserción del voto podría, en teoría, inferirse a partir de timestamps de logs del servidor. Resolver esto a nivel criptográfico (recibos sin coerción, *receipt-freeness*) excede el alcance de un proyecto académico, pero se documenta como limitación conocida.

## 6. ¿Por qué la cédula no se pre-registra en un padrón, sino que se registra "sobre la marcha"?

Se decidió que cualquier cédula nueva se registra automáticamente al primer intento de verificación, en lugar de requerir una lista cerrada de votantes habilitados de antemano. Esto simplifica el alcance del proyecto sin comprometer la regla central (bloqueo de doble voto), que es independiente de si existe o no un padrón previo.

## 7. ¿Por qué el estado de un votante puede ser `pendiente`, `voto` o `bloqueado`, y por qué el bloqueo es "perezoso"?

Inicialmente el estado se modeló como un booleano (`ya_voto`), pero esto no cubría el caso de alguien que registra su cédula y abandona el flujo sin completar el voto, dejando esa cédula "abierta" indefinidamente. Se añadió el estado `bloqueado`, activado por expiración de tiempo desde `hora_registro`.

El bloqueo se calcula de forma perezosa (en el momento de cada consulta, comparando la hora actual contra `hora_registro` más el tiempo límite configurado) en lugar de mediante un proceso en segundo plano que actualice la base de datos periódicamente. Se eligió este enfoque —el mismo patrón usado por tokens JWT u OTPs— porque evita añadir un scheduler/cron como pieza adicional de infraestructura, sin perder ninguna garantía: el sistema nunca deja pasar a votar a una cédula expirada, sin importar si su fila en la base de datos refleja activamente ese estado.

## 8. ¿Por qué un "voto nulo" por doble marcación no se modela en la base de datos?

En una papeleta física, marcar dos candidatos invalida el voto porque el papel no impone restricciones de selección. En esta interfaz web, el frontend usa controles de selección única (ej. radio buttons), por lo que es físicamente imposible que el usuario envíe dos selecciones a la vez — el problema se previene en la interfaz, no se modela como un estado adicional en `Voto`. Añadir esa columna sería complejidad sin función, dado que nunca se activaría con una interfaz bien construida.

El caso de expiración de tiempo (cédula que no llega a votar) tampoco genera una fila en `Voto`: simplemente no hay registro alguno, y la cédula queda marcada como `bloqueada` en `Votante`. Generar una fila de "voto nulo" correlacionada con una cédula específica que expiró reintroduciría el problema de trazabilidad que el diseño completo busca evitar (ver punto 5).

## 9. ¿Por qué `numero` de candidato es texto y no entero, y por qué su unicidad es solo dentro del partido?

`numero` se modeló como `VARCHAR` porque debe soportar formatos alfanuméricos como `"01A"` — un `INTEGER` perdería tanto los ceros a la izquierda como cualquier sufijo alfabético. La unicidad se definió como una restricción compuesta `UNIQUE(partido_id, numero)`, reflejando que en sistemas electorales reales el número de un candidato es relativo a su partido: el candidato #3 del Partido A y el #3 del Partido B coexisten sin conflicto.

## 10. ¿Por qué `ON DELETE RESTRICT` en lugar de `CASCADE`?

Tanto `Candidato → Partido` como `Voto → Candidato/Partido` usan `RESTRICT`. Se descartó `CASCADE` porque, en un dominio con implicaciones de integridad electoral, borrar un partido nunca debería arrastrar en cascada la pérdida silenciosa de sus candidatos y, peor, de los votos asociados a ellos. `RESTRICT` obliga a una decisión explícita y consciente (reasignar o borrar candidatos primero) antes de poder eliminar un partido.

## 11. ¿Por qué el logo del partido se guarda como archivo en disco y no como binario en la base de datos?

PostgreSQL no está optimizado para almacenar archivos binarios grandes: guardarlos como `BYTEA` infla la base de datos, ralentiza backups y obliga a traer el binario completo en consultas que no lo necesitan. Se optó por el patrón estándar de la industria: el archivo vive en disco (`static/logos/`), y la base de datos solo guarda la ruta (`logo_url`). El logo además es opcional al crear el partido — puede asociarse después mediante un endpoint dedicado (`PATCH /partidos/{id}/logo`).

## 12. ¿Por qué se descartó el patrón Prototype para la creación de entidades?

Se evaluó explícitamente el patrón Prototype para la creación de `Partido`, `Candidato`, `Voto` y `Votante`. Se descartó porque Prototype resuelve un problema que no existe en este dominio: clonar una instancia ya configurada cuando construirla desde cero es costoso. Las entidades del sistema son simples (pocos campos, sin estado complejo previo que valga la pena clonar), y no hay un caso de uso de negocio donde "clonar una entidad existente" tenga sentido — cada candidato o voto tiene identidad propia desde el principio.

En su lugar, se aplicó un **Factory Method** puntual en `VotoService._construir_voto()`, que centraliza la única decisión de creación que sí varía genuinamente según el tipo de entrada: cómo construir un voto según si llegó con `candidato_id` (el partido se deriva) o con `partido_id` directo (voto sin candidato).

## 13. ¿Por qué Docker para desarrollo local y Railway para la demo?

Docker garantiza que cualquiera que clone el repositorio reproduzca exactamente el mismo entorno (mismo PostgreSQL, misma configuración), sin depender de un servicio externo durante el desarrollo activo. Railway se usa en paralelo para tener una URL pública desplegada, de forma que un evaluador pueda probar el sistema sin instalar nada localmente. El mismo `Dockerfile` del backend se reutiliza para ambos entornos.

## 14. Nota sobre las dos ramas del repositorio

El enunciado original de este proyecto especifica, en su punto (a), que *"el modelo consta de las entidades: candidato, partido y votos"* — tres entidades, y el registro de un voto exige únicamente vincular candidato, partido y momento del voto. No se menciona control de identidad del votante en ningún punto del enunciado.

Durante el desarrollo se incorporó una cuarta entidad, `Votante`, junto con un flujo de verificación de cédula que bloquea el doble voto y preserva el secreto del voto (ver puntos 5, 6 y 7 de este documento). Esta decisión se tomó porque, en cualquier sistema que modele elecciones reales, la ausencia de control de unicidad de voto deja de ser un sistema electoral y pasa a ser solo un registro sin integridad — pero se reconoce con honestidad que **esta mejora no fue solicitada explícitamente en el enunciado**.

Para que el cumplimiento del enunciado literal sea verificable de forma independiente de esa mejora, el repositorio se organiza en dos ramas:

- **`main`**: la solución completa, con el control de votante activo. El parámetro `cedula` en `POST /votos` es opcional — si se envía, activa el control de unicidad; si no, el endpoint se comporta exactamente como en la rama base.
- **`feature/enunciado-base`**: una versión donde `POST /votos` no contempla ningún parámetro de cédula ni control de identidad, ciñéndose exactamente a lo que el enunciado pide: vincular candidato, partido y momento del voto.

La diferencia entre ambas ramas se concentra en tres archivos (`voto_service.py`, `voto_router.py`, `test_voto.py`) y no afecta el modelo de datos, la arquitectura en capas, los principios aplicados, ni el frontend, que son idénticos en ambas. Esto permite evaluar el proyecto desde cualquiera de las dos perspectivas: el cumplimiento estricto del enunciado, o la solución con mejoras de producto justificadas sobre él.

## 15. Autenticación: alcance futuro, no implementado

El proyecto no implementa autenticación ni autorización en ningún endpoint. Esto fue una decisión consciente de priorización (la autenticación era un criterio opcional, no obligatorio), no una omisión por desconocimiento. Se identificaron dos puntos de entrada distintos donde encajaría, si se retomara el proyecto:

**1. Protección de operaciones administrativas.** Las operaciones `POST`, `PUT` y `DELETE` de `/partidos` y `/candidatos` son actos de gestión electoral que en un sistema real solo debería poder ejecutar un administrador autenticado. La forma natural de incorporarlo en esta arquitectura sería:
- Un endpoint `POST /auth/login` que emita un JWT.
- Una dependencia de FastAPI (`Depends(verificar_token)`) inyectada únicamente en los routers administrativos, dejando los `GET` públicos (no tiene sentido exigir login solo para consultar información electoral pública).
- Una nueva capa `app/auth/` para el manejo de tokens, siguiendo el mismo patrón de inyección de dependencias ya usado para la sesión de base de datos (`get_db`).

**2. Verificación real de identidad del votante.** El flujo actual de `/votantes/verificar` confía en que la persona ingresa su propia cédula, sin ningún mecanismo que lo confirme — alguien podría ingresar la cédula de otra persona sin que el sistema lo detecte. Una autenticación real del votante (credenciales propias, o un token de un solo uso enviado por un canal externo) cerraría ese hueco. Es un problema distinto al de proteger endpoints administrativos: aquí se autentica al votante, no al operador del sistema.

Ambos mecanismos podrían coexistir sin conflicto, ya que protegen superficies distintas del sistema (gestión electoral vs. identidad del votante), y ninguno de los dos requeriría cambios en el modelo de datos actual.
