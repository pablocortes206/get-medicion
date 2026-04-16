



cual es el comando para ejecutar la apps de medidor de GET

Para ejecutar tu app de GET Wear Monitor (Streamlit), el comando base es este:

streamlit run app.py
🔧 En tu caso (según tu estructura típica)
Tú normalmente trabajas con scripts organizados, así que podría ser algo como:

cd D:\MIGRACION\00_ENTRADA_BRUTA\GET_APP
streamlit run app.py
o si el archivo tiene otro nombre:

streamlit run get_wear_monitor.py
🚀 Recomendación práctica (modo Pablo 😄)
Para que no pierdas tiempo cada vez:

Abre VS Code en la carpeta del proyecto

Abre terminal (Ctrl + ñ)

Ejecuta:

streamlit run app.py
⚠️ Si no parte (típicos problemas)
Streamlit no instalado:

pip install streamlit
Ambiente incorrecto:
(si usas venv)

.\venv\Scripts\activate
streamlit run app.py
Puerto ocupado:

streamlit run app.py --server.port 8502
Si quieres, en el siguiente paso te dejo un .bat automático tipo “joyita” para que hagas doble click y te levante la app sin escribir nada (ideal para faena).


Imagen cargada

El error de la foto dice que PowerShell no reconoce streamlit, o sea, pasa una de estas dos cosas:

Streamlit no está instalado

Está instalado, pero no en el Python/entorno que estás usando

Prueba así, en este orden.

Opción 1: ejecutarlo con Python
python -m streamlit run app.py --server.port 8502
Si no funciona, prueba:

py -m streamlit run app.py --server.port 8502
Si aparece que no está instalado
Instálalo con:

python -m pip install streamlit
o

py -m pip install streamlit
Y después vuelve a correr:

python -m streamlit run app.py --server.port 8502
Para revisar si tu Python está bien tomado
Ejecuta esto:

python --version
python -m pip --version
Si usas entorno virtual
Primero actívalo:

.\venv\Scripts\activate
Y luego:

python -m streamlit run app.py --server.port 8502
Importante
En tu terminal estás en:

C:\Users\hp
Así que además debes estar parado en la carpeta donde realmente está app.py. Por ejemplo:

cd "D:\ruta\de\tu\proyecto"
python -m streamlit run app.py --server.port 8502
Haz esta prueba exacta y me pegas lo que salga:

python -m streamlit run app.py --server.port 8502

Imagen cargada

Ya veo el problema clarito:
👉 No tienes ni Streamlit disponible ni el entorno virtual creado/activo, y además estás parado en la carpeta equivocada (C:\Users\hp).

Vamos directo al grano paso a paso (sin vueltas):

🔧 PASO 1 — Ir a la carpeta correcta del proyecto
Primero ubica dónde está tu app.py.

Ejemplo típico tuyo:

cd D:\MIGRACION\00_ENTRADA_BRUTA\GET_APP
Si no sabes dónde está:

dir app.py /s
🔧 PASO 2 — Crear entorno virtual (si no existe)
Ejecuta:

python -m venv venv
🔧 PASO 3 — Activar entorno (PowerShell correcto)
En PowerShell es así (no como lo escribiste):

.\venv\Scripts\Activate.ps1
👉 Si te tira error de permisos, ejecuta esto una sola vez:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Y repites activación.

🔧 PASO 4 — Instalar Streamlit
Con el entorno activado:

pip install streamlit
🚀 PASO 5 — Ejecutar la app (forma segura)
python -m streamlit run app.py --server.port 8502
🔥 RESUMEN EXPRESS (copia y pega)
cd D:\TU_RUTA\DEL_PROYECTO
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install streamlit
python -m streamlit run app.py --server.port 8502
💡 Lo que te pasó (explicado en simple)
streamlit no se reconoce → no está instalado o no está en PATH

.\venv\Scripts\activate no se reconoce → no existe ese venv

Estás en C:\Users\hp → ahí no está tu app

Si quieres, en el siguiente paso te dejo un .bat automático estilo operación faena (doble click y levanta todo solo, incluso crea el entorno si no existe).


Imagen cargada

Perfecto, ahora el problema cambió y está clarísimo 👇

👉 Error:

No existe ninguna unidad con el nombre 'D'
💥 Eso significa:
Tu PC NO tiene disco D:\ montado en este momento
(o cambió de letra, típico cuando usas OneDrive, USB, o particiones)

🔍 PASO 1 — Ver qué discos tienes
Ejecuta esto:

Get-PSDrive
👉 Te va a mostrar algo como:

C

E

F

etc.

🔍 PASO 2 — Buscar tu proyecto
Probablemente tu carpeta está en:

Opción A (muy común)
cd C:\Users\hp\Documents
Luego:

dir
Opción B (buscar directo el archivo)
dir app.py /s
💡 Esto te dirá EXACTAMENTE dónde está tu app.

🔧 PASO 3 — Ir a la ruta correcta
Ejemplo (ajústalo a lo que encuentres):

cd "C:\Users\hp\Documents\GET_APP"
🚀 PASO 4 — Ejecutar sin errores
Cuando ya estés en la carpeta correcta:

python -m streamlit run app.py
🧠 Traducción simple (modo terreno)
❌ D:\ no existe → estás apuntando a un disco que no está

❌ No encuentra app → estás parado en la carpeta equivocada

✅ Primero ubica el archivo → después ejecuta

🔥 Haz esto ahora y me pegas resultado
Get-PSDrive
y después:

dir app.py /s
Con eso te dejo funcionando la app sí o sí 👍


Imagen cargada

Bien, ya encontramos una carpeta del proyecto:

C:\Users\hp\Documents\CAEX_Component_Manager
Ahora entra ahí y revisa qué archivos tiene:

cd "C:\Users\hp\Documents\CAEX_Component_Manager"
dir
Busca un archivo como:

app.py

main.py

inicio.py

o algo .py

Si aparece app.py
Ejecuta esto:

python -m streamlit run app.py --server.port 8502
Si aparece otro nombre, por ejemplo main.py
Entonces sería:

python -m streamlit run main.py --server.port 8502
Si te dice que no tiene streamlit instalado
Instálalo ahí mismo:

python -m pip install streamlit
y luego vuelve a correr el comando.

Haz estos dos comandos ahora y pégame el resultado:

cd "C:\Users\hp\Documents\CAEX_Component_Manager"
dir

Imagen cargada

Ya veo exactamente dónde está el problema 👇
👉 Estás escribiendo la ruta sin el comando cd, por eso PowerShell intenta ejecutarla como si fuera un programa.

🔥 CORRECCIÓN CLARA
En vez de esto ❌:

C:\Users\hp\Documents\CAEX_Component_Manager
Debes escribir esto ✅:

cd "C:\Users\hp\Documents\CAEX_Component_Manager"
🚀 SECUENCIA CORRECTA (haz esto tal cual)
cd "C:\Users\hp\Documents\CAEX_Component_Manager"
dir
👉 Aquí queremos ver si existe:

app.py

u otro .py

🔧 DESPUÉS (IMPORTANTE)
No uses streamlit directo (no lo tienes en PATH).

Usa este sí o sí:

python -m streamlit run app.py --server.port 8502
⚠️ SI FALLA
Instala streamlit:

python -m pip install streamlit
🧠 TRADUCCIÓN SIMPLE
❌ Escribiste la ruta sola → PowerShell no la entiende

✅ Usa cd para moverte

❌ streamlit solo → no existe en tu entorno

✅ python -m streamlit → siempre funciona

👇 Haz esto ahora
cd "C:\Users\hp\Documents\CAEX_Component_Manager"
dir
y mándame la salida. Con eso ya te dejo corriendo la app sí o sí 👍


Imagen cargada

Perfecto 👌 ya estamos listos, lo hiciste bien.

Veo que tienes:

app.py
en la carpeta correcta ✅

🚀 AHORA SOLO FALTA 1 COSA
Ejecuta esto:

python -m streamlit run app.py --server.port 8502
🔴 Si te tira error (seguro falta streamlit)
Instálalo:

python -m pip install streamlit
Y después:

python -m streamlit run app.py --server.port 8502
✅ Resultado esperado
Te debería abrir automáticamente algo como:

Local URL: http://localhost:8502
👉 Se abre en el navegador tu app GET

🧠 Nota rápida (importante)
No uses más:

streamlit run app.py
porque tu sistema no lo reconoce.

👉 SIEMPRE usa:

python -m streamlit run app.py
🔥 Si quieres nivel PRO (recomendado)
Te puedo dejar un .bat tipo faena:

doble click

levanta la app

instala todo si falta

Solo dime: “hazme el bat” 😄


Imagen cargada

Bien Pablo, ya lograste levantar Streamlit 👍
Pero esa pantalla negra significa una de estas dos cosas:

🔎 🔴 PROBLEMA MÁS PROBABLE
👉 Tu app.py está vacío o no tiene contenido ejecutable

En tu dir vimos:

Length: 0
💥 Eso significa:
el archivo está vacío (0 bytes) → por eso no muestra nada

🔧 SOLUCIÓN INMEDIATA
1️⃣ Abre el archivo
En VS Code:

Abre app.py

2️⃣ Pega esto (prueba base)
import streamlit as st

st.title("GET Wear Monitor 🚜")

st.write("App funcionando correctamente")
3️⃣ Guarda (Ctrl + S)
🔄 Streamlit se actualiza solo
No necesitas reiniciar, pero si no carga:

Ctrl + C
python -m streamlit run app.py --server.port 8502
✅ Resultado esperado
Ahora deberías ver en el navegador:

👉 GET Wear Monitor 🚜
👉 texto de prueba

🧠 Traducción simple
La app sí corre ✅

Pero el archivo está vacío ❌

Streamlit no tiene nada que mostrar

🔥 Siguiente paso (si quieres)
Te puedo:

reconstruir tu app GET completa (con BD, desgaste, proyección)

dejarla lista estilo Teck (visual + lógica)

o recuperar código si lo perdiste

Solo dime:
👉 “armemos la app completa” o “recupera el GET Wear Monitor”


Imagen cargada
vmira este es el link

Sí, ese es el link:

get-medicion-get.streamlit.app
Si ahí te aparece la página en blanco, normalmente pasa por una de estas razones:

Lo más probable
Tu app sí está publicada, pero está fallando al cargar por dentro. En Streamlit Cloud suele pasar cuando:

falta algún paquete en requirements.txt

el archivo principal no es el correcto

hay error al leer la base de datos o un archivo Excel

la app intenta abrir una ruta local de tu PC, como C:\...

hay un error de Python apenas inicia

Qué revisar ahora
En Streamlit Cloud entra al panel de esa app y revisa:

Manage app

Logs

Settings

Main file path

Lo clave
Revisa que el archivo principal sea realmente algo como:

app.py
y no otro nombre.

También confirma que en el repositorio existan:

app.py

requirements.txt

Si quieres probar rápido
Dentro de app.py, deja temporalmente esto:

import streamlit as st

st.title("GET Wear Monitor")
st.write("App publicada correctamente")
Si con eso carga, el problema no es Streamlit Cloud, sino tu código anterior.

Errores típicos que dejan pantalla blanca
usar archivos locales como:

"C:\\Users\\hp\\Documents\\..."
abrir una base de datos que no subiste al repo

usar imágenes, logos o excels que no están en GitHub

librerías no instaladas en requirements.txt

Lo que necesito para ayudarte bien
Pégame una de estas dos cosas:

el error de Logs de Streamlit Cloud, o

el contenido de tu app.py

Con eso te digo exactamente qué está rompiendo la app.


porque claude en plan pro me dice Has agotado tu uso adicional ∙ Tu límite se restablece a las 15:00

Porque incluso en Claude Pro (de ) hay límites de uso, no es ilimitado.

Te explico claro 👇

🔴 ¿Qué significa ese mensaje?
“Has agotado tu uso adicional”

👉 Significa que:

Ya consumiste el cupo de uso del modelo (tokens/mensajes) en ese periodo

Entraste al modo limitado (rate limit)

Y por eso te dice:
👉 “Tu límite se restablece a las 15:00”

⚙️ Cómo funcionan esos límites
En Claude Pro:

Tienes más capacidad que el plan gratis

Pero sigue habiendo restricciones como:

Cantidad de mensajes

Tamaño de prompts (tokens)

Uso intensivo (código, archivos grandes, etc.)

💡 Si haces cosas como:

subir PDFs grandes

trabajar con código (como tu app GET)

hacer muchas iteraciones seguidas

👉 consumes el cupo más rápido

🧠 Traducción simple (modo terreno)
❌ No es ilimitado

⚠️ Le metiste harto uso (probablemente desarrollo + pruebas)

🕒 Ahora estás en “tiempo fuera” hasta que reinicie

🔄 ¿Cada cuánto se reinicia?
Depende del tipo de límite:

algunos son por horas

otros por día

Ese mensaje específico:
👉 es un límite temporal (rate limit por carga de uso)

💡 Cómo evitar que pase tanto
Evita mandar archivos muy grandes repetidamente

No hagas muchas pruebas seguidas sin optimizar

Divide el trabajo (ej: código por partes)

🟢 Comparación rápida
Claude Pro → más potente en análisis, pero con límites dinámicos

ChatGPT Plus (acá) → más estable para uso continuo

Si quieres, te digo exactamente:
👉 cuánto estás consumiendo con tu tipo de uso (apps, código, etc.)
y cómo optimizar para que no te vuelva a bloquear.



Pegado text.txt
Documento
esta el la ultima parte de URL de base de datos puedes ayudarme a continuar

Sí Pablo, entendí perfecto todo tu flujo y el problema 👍
Te resumo claro para validar que estamos alineados:

🧠 🔥 TU PROBLEMA REAL (CLAVE)
Según tu código y lo que explicaste 


👉 Estás usando:

DB_PATH = "mediciones.db"
💥 Eso en Streamlit Cloud = muerte segura de los datos

Porque:

La app se “duerme”

El servidor se reinicia

👉 el archivo .db se borra

→ pierdes todo historial

🟢 LO QUE QUIERES LOGRAR
✅ Que los datos NO se borren

✅ Poder cargar Excel de horómetros

✅ Calcular tasa de desgaste real (mm/h)

✅ Manejar cambios de GET (reset ciclo)

✅ Después → dashboard (críticos, proyección, etc.)

🟡 DÓNDE ESTÁS AHORA
Ya hiciste:

✔ App corriendo en Streamlit Cloud

✔ Código actualizado

✔ Supabase creado

✔ Estás buscando la URL (te falta eso)

🔧 TE AYUDO CON EL PASO DONDE ESTÁS PEGADO
📍 DÓNDE ENCONTRAR LA URL DE SUPABASE
Haz esto:

En Supabase (donde estás ahora)

Menú izquierdo → ⚙️ Settings

Click en General

Ahí verás algo como:

Project URL:
https://abcxyz123.supabase.co
👉 ESA es la URL que necesitas

🔑 LO QUE DEBES TENER ANOTADO
En tu bloc de notas:

✅ URL

✅ anon key

✅ service_role key

🚨 IMPORTANTE (te lo adelanto para el siguiente paso)
Después vamos a hacer esto en tu app:

from supabase import create_client

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)
🧭 SIGUIENTE PASO (cuando tengas la URL)
Dime:

👉 “ya tengo URL + keys”

Y te guío paso a paso para:

🔥 Migrar tu app COMPLETA a Supabase
sin perder estructura

sin romper tu lógica

dejando persistencia real

🧠 Nota importante (te ahorro errores típicos)
NO subas la service_role a GitHub

usamos st.secrets (te enseño)

tu SQLite se elimina completamente

Vas perfecto 👊
Este es el paso más importante de toda la app.

Avísame cuando tengas la URL 👍


Imagen cargada
ves la URL

Sí 👌 ya la veo perfecto.

👉 Tu Project ID es:

sbxkrkeoqfgsgcjutikj
👉 Por lo tanto tu URL real de Supabase es:

https://sbxkrkeoqfgsgcjutikj.supabase.co
🔥 LISTO — YA TENEMOS TODO
Ahora tienes:

✅ URL → https://sbxkrkeoqfgsgcjutikj.supabase.co

✅ anon key → (la copiaste antes)

✅ service_role → (la copiaste antes)

🚀 SIGUIENTE PASO (CRÍTICO)
Ahora vamos a conectar tu app con Supabase
👉 sin romper lo que ya hiciste

🧩 PASO 4 — Agregar secrets en Streamlit
Ve a tu app en Streamlit Cloud

Click en ⚙️ Settings

Busca Secrets

Pega esto:

SUPABASE_URL = "https://sbxkrkeoqfgsgcjutikj.supabase.co"
SUPABASE_KEY = "TU_ANON_KEY"
⚠️ IMPORTANTE:

usa anon key, NO el service_role aquí

🧠 ¿Por qué?
anon → seguro para apps públicas

service_role → solo backend (no se usa aquí)

🧩 PASO 5 — Instalar librería en tu app
En tu repo GitHub agrega (o edita) archivo:

requirements.txt
y agrega:

supabase
🧩 PASO 6 — Cambiar conexión en tu código
En tu app.py, reemplaza SQLite por esto:

from supabase import create_client
import streamlit as st

@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()
⚠️ IMPORTANTE (lo más crítico de todo)
👉 Aún NO hemos creado las tablas en Supabase
👉 Eso es el siguiente paso

🧭 SIGUIENTE PASO
Dime:

👉 “ya cargué secrets y requirements”

y te voy a:

🔥 Crear la base de datos completa
tabla mediciones

tabla cambios GET

estructura lista para producción

Vas excelente 👊
Este paso ya te saca del problema de pérdida de datos para siempre.


Imagen cargada
tengo todo en block de notas

Sí, ya tienes todo lo necesario. No pegues esas claves aquí de nuevo.

Como en la captura aparece la service_role, te conviene rotarla después por seguridad. La anon se usa en la app; la service_role no.

Paso 1: cargar los secrets en Streamlit
En tu app de Streamlit Cloud:

Entra a la app

Ve a Settings

Abre Secrets

Pega esto, reemplazando solo la clave anon:

SUPABASE_URL = "https://sbxkrkeoqfgsgcjutikj.supabase.co"
SUPABASE_KEY = "AQUI_PEGA_TU_ANON_KEY"
Guarda.

Paso 2: agregar dependencia
En GitHub, abre tu requirements.txt.

Si existe, agrega una línea:

supabase
Si no existe, créalo con:

streamlit
pandas
supabase
openpyxl
Paso 3: cambiar la conexión en app.py
En tu app.py, agrega esto cerca de los imports:

from supabase import create_client
Y luego agrega esta función:

@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()
Paso 4: detener el uso de SQLite
Busca algo como:

DB_PATH = "mediciones.db"
y cualquier función con:

sqlite3.connect(...)

CREATE TABLE

INSERT INTO

SELECT * FROM

Eso lo vamos a reemplazar en el siguiente paso por consultas a Supabase.

Importante
No uses la service_role en Streamlit Cloud. Usa solo la anon.

Y como esa service_role quedó visible en la captura, después en Supabase ve a:
Settings → API Keys / Secrets
y genera una nueva.

Cuando termines, dime: “ya cargué secrets y requirements”.


Imagen cargada

Perfecto Pablo 👌 ya estás en el punto exacto para dejar esto profesional de verdad.

Veo en tu repo:

✅ app.py

⚠️ mediciones.db (esto después lo eliminamos)

⚠️ requirements.txt (hay que ajustarlo)

🔥 PASO A PASO (sin saltos)
✅ PASO 1 — Crear / editar requirements.txt
Haz clic en requirements.txt (lado izquierdo en GitHub)

Luego en ✏️ editar y deja esto:

streamlit
pandas
supabase
openpyxl
👉 Después:

Click en Commit changes

✅ PASO 2 — Agregar conexión a Supabase
En tu app.py, arriba donde están los imports agrega:

from supabase import create_client
🔧 Luego pega esto justo después de los imports:
@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()
👉 Commit changes

⚠️ PASO 3 — NO BORRES SQLite TODAVÍA
Todavía NO toques:

sqlite3
DB_PATH
Primero vamos a crear la base en Supabase.

🚀 PASO 4 — Crear tablas en Supabase
En Supabase:

👉 Menú izquierdo → SQL Editor

👉 Click en New query

👉 pega esto:

create table mediciones (
    id uuid primary key default gen_random_uuid(),
    equipo text,
    fecha date,
    horometro numeric,
    mm_izq numeric,
    mm_der numeric,
    usuario text,
    creado_en timestamp default now()
);

create table cambios_get (
    id uuid primary key default gen_random_uuid(),
    equipo text,
    fecha date,
    horometro numeric,
    mm_final_izq numeric,
    mm_final_der numeric,
    motivo text,
    tecnico_1 text,
    tecnico_2 text,
    observaciones text,
    creado_en timestamp default now()
);
👉 Click Run

🔥 PASO 5 — Validar conexión (simple)
Antes de migrar todo, prueba esto en tu app.py:

st.write("Conectado a Supabase:", supabase is not None)
🧠 LO QUE ESTAMOS HACIENDO (importante que lo entiendas)
Antes:

Streamlit → archivo .db local → se borra
Ahora:

Streamlit → Supabase (cloud) → PERMANENTE
🚨 SIGUIENTE PASO (cuando hagas esto)
Dime:

👉 “ya cree tablas y conecte supabase”

y ahí te hago lo más importante:

🔥 Migrar TU lógica actual (sin romper nada)
reemplazar INSERT sqlite → supabase

reemplazar SELECT → supabase

mantener TODA tu app igual

Vas excelente 👊
Este es el paso que convierte tu app en nivel producción minería real.


Imagen cargada
ahi en APP.py

Perfecto 👌 estás justo donde hay que trabajar.

Vamos paso a paso dentro de ese mismo app.py.

🔧 PASO 1 — Agregar import de Supabase
Arriba donde tienes esto:

import pandas as pd
import streamlit as st
👇 DEBAJO agrega:

from supabase import create_client
🔧 PASO 2 — Crear conexión
Baja unas líneas después de los imports (antes de tu estilo TECK)
y pega esto:

@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()
🔧 PASO 3 — Guardar
👉 Click en Commit changes

🧪 PASO 4 — Probar conexión (rápido)
Agrega temporalmente esto en cualquier parte:

st.write("Supabase OK:", supabase is not None)
👉 Commit changes
👉 Espera que Streamlit actualice

✅ RESULTADO ESPERADO
En tu app deberías ver:

Supabase OK: True
⚠️ SI FALLA
Probablemente:

no cargaste los secrets

o falta supabase en requirements.txt

🚨 IMPORTANTE (NO HAGAS ESTO AÚN)
No borres todavía:

sqlite3
mediciones.db
Primero validamos conexión.

🧭 SIGUIENTE PASO
Cuando veas:

👉 Supabase OK: True

me dices:

“listo conectado”

y ahí hacemos lo más importante:

🔥 Migrar tu app completa sin perder lógica
(te dejo los insert/select ya listos)

Vas perfecto 👊
Este es el punto donde pasas de app de prueba → app profesional real.


Imagen cargada
así?

Sí Pablo 👏 está perfecto así. Bien ejecutado.

Lo que tienes ahora:

✅ Import correcto

✅ Función cacheada

✅ Lectura de st.secrets

✅ Cliente Supabase inicializado

👉 Este bloque está 100% bien.

🔥 AHORA VIENE LA PRUEBA CLAVE
Agrega esto debajo de donde creaste supabase:

st.write("Supabase OK:", supabase is not None)
👉 Haz Commit changes

⏱️ ESPERA
Streamlit se va a actualizar solo (30–60 segundos)

✅ RESULTADO ESPERADO
En tu app debería aparecer:

Supabase OK: True
⚠️ SI NO APARECE
Entonces el problema está en:

1. Secrets no cargados
Revisa en Streamlit:

Settings → Secrets
Debe estar EXACTO así:

SUPABASE_URL = "https://sbxkrkeoqfgsgcjutikj.supabase.co"
SUPABASE_KEY = "TU_ANON_KEY"
2. requirements.txt
Debe tener:

supabase
🧠 IMPORTANTE (te explico corto)
Hasta ahora:

Solo creamos la conexión ✔

Aún NO guardamos datos ahí ❌

🚀 SIGUIENTE PASO
Cuando veas:

👉 Supabase OK: True

me dices:

“listo conectado”

y ahí viene lo bueno:

🔥 Te migro tu app completa
guardar mediciones en Supabase

guardar cambios GET

dejar de usar SQLite

y NO pierdes nada de lógica

Vas excelente 👊
Ya pasaste lo más difícil.


st.write("Supabase OK:", supabase is not None) esto donde se pega?

Buena pregunta 👍 te explico claro para que no te pierdas.

📍 DÓNDE PEGARLO
En tu código tienes esto:

supabase = get_supabase()
👉 JUSTO DEBAJO de esa línea pega esto:

st.write("Supabase OK:", supabase is not None)
🔧 Te debería quedar así:
supabase = get_supabase()

st.write("Supabase OK:", supabase is not None)
🚀 Luego
Click en Commit changes

Espera que la app se actualice

Abre tu app

✅ Qué deberías ver
En la pantalla:

Supabase OK: True
🧠 Si no aparece
Me mandas captura y lo vemos al tiro.

Haz eso y dime qué te aparece 👊


pero voy a Visual studio Code? o get medicion

Hazlo en GitHub, en el archivo app.py de get-medicion, donde ya estás editando.

No en VS Code por ahora.

O sea:

En la página de GitHub de get-medicion

Abre app.py

Click en Edit

Debajo de:

supabase = get_supabase()
pega:

st.write("Supabase OK:", supabase is not None)
Commit changes

Espera que Streamlit actualice

Después revisas la app. Si aparece Supabase OK: True, seguimos.


Imagen cargada

Perfecto 👏👏👏
👉 Está EXACTAMENTE donde corresponde. Muy bien hecho.

🚀 AHORA SOLO FALTA
👉 Click en Commit changes

⏱️ Luego
Espera 30–60 segundos

Abre tu app:
👉 get-medicion-get.streamlit.app

✅ DEBERÍAS VER
Supabase OK: True
🔴 SI VES False O ERROR
Me mandas captura y lo arreglamos al tiro.

🔥 CUANDO VEAS TRUE
Me dices:

👉 “listo conectado”

y ahí pasamos al paso más importante:

💣 Migrar tu app completa a Supabase
(sin perder nada de lo que ya hiciste)

Vas perfecto Pablo 👊
Este es el punto donde ya estás a nivel app real de operación.


Imagen cargada

Perfecto, ya encontramos el problema exacto.

El error dice que no existe esta clave en Streamlit:

SUPABASE_URL
O sea, el código está bien, pero los Secrets no están cargados o no se guardaron.

Haz esto
En Streamlit Cloud:

Abre la app

Ve a Settings

Entra a Secrets

Pega esto:

SUPABASE_URL = "https://sbxkrkeoqfgsgcjutikj.supabase.co"
SUPABASE_KEY = "AQUI_PEGA_TU_ANON_KEY"
Guarda

Ojo con esto
Tiene que quedar exactamente así:

SUPABASE_URL

SUPABASE_KEY

Todo en mayúsculas, sin espacios extras, sin comillas raras.

Después
Espera un poco y recarga la app.

Si quedó bien, debería dejar de salir el KeyError y mostrar:

Supabase OK: True
No cambies app.py ahora. El problema no está en el código, está en Secrets.

Cuando lo guardes, mándame captura de la pantalla de Secrets.


Imagen cargada

Estás en GitHub, pero el error es de Streamlit Cloud 👇
👉 Los secrets NO se configuran en GitHub, se configuran en la app de Streamlit.

🔴 AQUÍ ESTÁ EL ERROR
Tu app busca:

st.secrets["SUPABASE_URL"]
💥 Pero en Streamlit Cloud no existe, por eso el KeyError.

✅ DÓNDE DEBES IR (IMPORTANTE)
👉 Abre tu app:

get-medicion-get.streamlit.app
Luego:

Abajo a la derecha → click en ⚙️ Manage app

Se abre panel

Click en Settings

Click en Secrets

🔧 AHÍ PEGA ESTO
SUPABASE_URL = "https://sbxkrkeoqfgsgcjutikj.supabase.co"
SUPABASE_KEY = "AQUI_PEGA_TU_ANON_KEY"
⚠️ ERRORES TÍPICOS
No hacer esto:

❌ pegar en GitHub (como ahora)

❌ usar service_role

❌ escribir supabase_url en minúscula

Debe ser EXACTO:

SUPABASE_URL

SUPABASE_KEY

🚀 DESPUÉS
Guarda

Espera 30 segundos

Recarga la app

✅ RESULTADO
Debe desaparecer el error y ver:

Supabase OK: True
🧭 SI NO ENCUENTRAS “Manage app”
Mándame captura de:
👉 la pantalla de tu app abierta (completa)

y te marco exactamente dónde hacer click.

Tranquilo 👊 estás a 1 paso de dejar esto funcionando real.


Imagen cargada

Perfecto 👌 estás en el lugar correcto… pero hay un detalle que está rompiendo todo.

🔴 EL PROBLEMA
Tienes esto:

SUPABASE_KEY = "AQUI_PEGA_TU_ANON_KEY"
💥 Eso es solo un texto de ejemplo
👉 no es la clave real

✅ SOLUCIÓN (rápida)
Vuelve a Supabase

Ve a:
👉 Settings → API Keys

Copia la clave que dice:

anon public
🔧 REEMPLAZA ESTO
De:

SUPABASE_KEY = "AQUI_PEGA_TU_ANON_KEY"
A algo así (ejemplo):

SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
⚠️ IMPORTANTE
❌ NO uses service_role

✅ SOLO usa anon

🚀 DESPUÉS
Click en Save changes

Espera 30–60 segundos

Recarga la app

✅ RESULTADO ESPERADO
Debe desaparecer el error y ver:

Supabase OK: True
🔥 CUANDO TE FUNCIONE
Me dices:

👉 “listo conectado”

y pasamos al paso potente:

💣 Migrar tu app completa (guardar datos reales en la nube)
Vas excelente 👊
Este es el último paso crítico antes de dejar la app nivel producción real.


Imagen cargada

Perfecto Pablo 👏👏 ahora sí está bien configurado.

👉 Ya tienes:

✅ SUPABASE_URL

✅ SUPABASE_KEY (anon real)

✅ formato correcto

🚀 AHORA HAZ ESTO
Click en Save changes (abajo a la derecha)

Espera ~30–60 segundos

Recarga tu app:
👉 get-medicion-get.streamlit.app

✅ RESULTADO ESPERADO
Debe desaparecer el error rojo y ver:

Supabase OK: True
⚠️ SI AÚN FALLA
Haz un refresh fuerte:

Ctrl + F5
🔐 IMPORTANTE (seguridad)
Como mostraste la clave en la captura:
👉 Después te recomiendo:

Ir a Supabase

Regenerar la anon key

(No es crítico ahora, pero sí buena práctica)

🧭 SIGUIENTE PASO
Cuando veas:

👉 Supabase OK: True

me dices:

“listo conectado”

y pasamos a lo más importante:

💣 Migrar tu app completa
guardar mediciones reales

guardar cambios GET

eliminar SQLite

dejar persistencia total

Vas excelente 👊
Ya estás a un paso de tener una app de nivel industrial.


sabes que  no veo la fecha cuando de hace la medicion que va de la mano con el horometro

Sí, te entendí.
En la app debe verse claramente la fecha de la medición, porque esa fecha va amarrada al horómetro y después sirve para:

calcular tasa de desgaste

ordenar historial

proyectar cambio

cruzar con los horómetros diarios

Ahora probablemente la app está guardando la fecha por detrás o no la está mostrando bien en el formulario/historial.

Lo correcto
En el formulario de ingreso de medición deberías tener un campo visible así:

fecha_medicion = st.date_input("Fecha de medición", value=date.today())
horometro = st.number_input("Horómetro", min_value=0.0, step=1.0)
Y al guardar, esa fecha_medicion debe ir junto con el horómetro.

También debe verse en el historial
En la tabla de historial deberían aparecer al menos estas columnas:

Equipo

Fecha medición

Horómetro

mm izq

mm der

% desgaste

usuario

Mi recomendación
Haz dos mejoras:

1. En el formulario
Agregar arriba del horómetro:

fecha_medicion = st.date_input("Fecha de medición", value=date.today())
2. En la tabla historial
Mostrar la columna fecha como una de las primeras.

Ojo importante
Si estás usando el Excel de horómetros diarios, esa fecha es todavía más crítica, porque la lógica debiera ser:

fecha de medición + horómetro de ese día = base real del cálculo

No solo el horómetro suelto.

Cómo debería verse idealmente
Algo así en el ingreso:

with st.form("form_medicion"):
    equipo = st.selectbox("Equipo", equipos)
    fecha_medicion = st.date_input("Fecha de medición", value=date.today())
    horometro = st.number_input("Horómetro del equipo", min_value=0.0, step=1.0)
    mm_izq = st.number_input("Medición IZQ (mm)", min_value=0.0, step=1.0)
    mm_der = st.number_input("Medición DER (mm)", min_value=0.0, step=1.0)
    usuario = st.text_input("Usuario")
    guardar = st.form_submit_button("Guardar medición")
Y al guardar:

"fecha": str(fecha_medicion)
Lo que te propongo
El siguiente ajuste debería ser:
ordenar el formulario para que quede visible y lógico:

Equipo

Fecha de medición

Horómetro

mm izq

mm der

usuario

Si quieres, te doy el bloque exacto para pegar en tu app.py y dejar visible la fecha en el formulario y en el historial.


cambia ubicacion por fecha no le veo importacia

Buena decisión 👍 — mucho más sentido operacional usar fecha que ubicación.

Vamos directo a lo práctico, sin romper tu app.

🔧 CAMBIO: UBICACIÓN → FECHA
🟢 1. Buscar en tu código
En app.py busca algo como:

ubicacion = st.text_input("Ubicación")
o:

st.text_input("Ubicación")
🔁 2. Reemplazar por FECHA
Cámbialo por esto:

fecha = st.date_input("Fecha de medición", value=date.today())
🟢 3. Ajustar guardado
Donde estás guardando datos (SQLite o Supabase), busca algo como:

"ubicacion": ubicacion
y reemplázalo por:

"fecha": str(fecha)
🟢 4. Si usas SQLite (por ahora)
Asegúrate que tu tabla tenga columna fecha

Si no existe, después la arreglamos en la migración a Supabase.

🟢 5. Mostrar en historial
Busca donde muestras la tabla (st.dataframe o st.table)
y asegúrate que incluya fecha.

Ejemplo:

df = df[["equipo", "fecha", "horometro", "mm_izq", "mm_der"]]
st.dataframe(df)
🧠 POR QUÉ ESTE CAMBIO ES CLAVE
Antes:

Ubicación → no aporta al modelo
Ahora:

Fecha + Horómetro → base para:
- tasa desgaste (mm/h)
- proyección
- correlación con Excel
🔥 NIVEL PRO (te lo dejo adelantado)
Después vamos a hacer:

👉 si no ingresas horómetro
→ la app lo toma desde Excel según fecha

Eso te deja el sistema automático completo.

🚀 SIGUIENTE
Haz el cambio y dime:

👉 “listo cambio fecha”

y después te ayudo a:

💣 conectar fecha + horómetro + Excel
(esto es lo que realmente le da valor a la app)

Vas muy bien 👊
Este tipo de decisiones son las que hacen que la app sirva en terreno de verdad.


Te paso el codigo y lo modificas si hay que hacer algo mas tambien te parecer 

Sí, pásamelo y te lo dejo ajustado.

Mándame el app.py completo o pégalo por partes si es muy largo.
Con eso te hago:

cambio de Ubicación → Fecha de medición

revisión de flujo completo

detección de mejoras necesarias

y te digo qué más conviene corregir ahora para no retrabajar después

Si puedes, pega también el bloque donde:

se arma el formulario

se guardan los datos

se muestra el historial

Así avanzo más rápido.



Pegado text(1).txt
Documento


Pensó durante 7s
Sí. Ya lo revisé y entendí bien cómo está armado. Tu app hoy todavía guarda en SQLite, aunque ya abre conexión a Supabase; además el campo “Ubicación” sigue vivo en formulario, tabla y DB, y la fecha real de medición no la estás capturando desde el usuario, sino que la tomas con datetime.now() al guardar. 


El cambio que te recomiendo hacer ahora es este:

Qué cambiaría de inmediato
Reemplazar “Ubicación” por “Fecha de medición”

Guardar esa fecha junto al horómetro

Mostrar la fecha en historial y flota

Quitar el texto temporal Supabase OK

No tocar todavía toda la lógica a Supabase hasta dejar correcto el flujo de medición

Lo importante que vi en tu código
En tu función guardar_medicion(...) todavía recibes ubicacion y guardas fecha con now.isoformat(...), o sea, con la hora actual del servidor, no con la fecha que el técnico realmente midió. También la tabla mediciones tiene la columna ubicacion y el formulario del tab “Ingreso Medición” sigue usando st.text_input("Ubicación (opcional)"). 


Cambios exactos
1) Cambia la estructura de la tabla
En init_db() reemplaza este bloque de mediciones por este:

con.execute("""
CREATE TABLE IF NOT EXISTS mediciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    equipo TEXT NOT NULL,
    usuario TEXT,
    componente TEXT,
    mm REAL,
    horometro REAL,
    mm_izq REAL,
    mm_der REAL,
    mm_usada REAL,
    condicion_pct REAL,
    estado TEXT,
    accion TEXT,
    tasa_mm_h REAL,
    horas_a_critico REAL,
    dias_a_critico REAL,
    semana_medicion INTEGER,
    semana_label TEXT,
    inicio_semana TEXT,
    fin_semana TEXT,
    es_cambio INTEGER DEFAULT 0
)
""")
2) Quita ubicacion de la migración
En migrar_db_agregar_columnas() elimina esta línea:

"ubicacion": "ubicacion TEXT",
3) Cambia la función guardar_medicion
Reemplázala completa por esta:

def guardar_medicion(
    fecha_medicion, equipo, usuario, horometro,
    mm_izq, mm_der, mm_usada, desgaste_pct,
    estado, accion, tasa_mm_h, horas_a_critico, dias_a_critico,
):
    fecha_dt = datetime.combine(fecha_medicion, datetime.now().time())
    semana, semana_label, ini_sem, fin_sem = calcular_semana_medicion(fecha_dt)

    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            INSERT INTO mediciones (
                fecha, equipo, usuario, componente, mm,
                horometro, mm_izq, mm_der, mm_usada,
                condicion_pct, estado, accion,
                tasa_mm_h, horas_a_critico, dias_a_critico,
                semana_medicion, semana_label, inicio_semana, fin_semana,
                es_cambio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            fecha_dt.isoformat(timespec="seconds"),
            equipo,
            (usuario or "").strip() or None,
            "Cuchilla",
            float(mm_usada),
            float(horometro),
            float(mm_izq),
            float(mm_der),
            float(mm_usada),
            float(desgaste_pct),
            estado,
            accion,
            float(tasa_mm_h) if tasa_mm_h is not None else None,
            float(horas_a_critico) if horas_a_critico is not None else None,
            float(dias_a_critico) if dias_a_critico is not None else None,
            int(semana),
            semana_label,
            ini_sem.isoformat(),
            fin_sem.isoformat(),
        ))
        con.commit()
4) Cambia el formulario del tab “Ingreso Medición”
En este bloque:

equipo = st.selectbox("Equipo", EQUIPOS, index=0, key="eq_med")
ubicacion = st.text_input("Ubicación (opcional)", value="", key="ub_med")
usuario = st.text_input("Usuario (Técnico)", value="", key="us_med")
reemplázalo por:

equipo = st.selectbox("Equipo", EQUIPOS, index=0, key="eq_med")
fecha_medicion = st.date_input("Fecha de medición", value=date.today(), key="fc_med")
usuario = st.text_input("Usuario (Técnico)", value="", key="us_med")
5) Cambia la llamada a guardar
Reemplaza esto:

guardar_medicion(
    equipo=equipo, ubicacion=ubicacion, usuario=usuario,
    horometro=res.horometro, mm_izq=res.mm_izq, mm_der=res.mm_der,
    mm_usada=res.mm_usada, desgaste_pct=res.desgaste_pct,
    estado=res.estado, accion=res.accion,
    tasa_mm_h=res.tasa_mm_h,
    horas_a_critico=res.horas_a_critico,
    dias_a_critico=res.dias_a_critico,
)
por esto:

guardar_medicion(
    fecha_medicion=fecha_medicion,
    equipo=equipo,
    usuario=usuario,
    horometro=res.horometro,
    mm_izq=res.mm_izq,
    mm_der=res.mm_der,
    mm_usada=res.mm_usada,
    desgaste_pct=res.desgaste_pct,
    estado=res.estado,
    accion=res.accion,
    tasa_mm_h=res.tasa_mm_h,
    horas_a_critico=res.horas_a_critico,
    dias_a_critico=res.dias_a_critico,
)
6) Quita ubicacion del historial
En cargar_historial() cambia el SELECT desde:

SELECT id, fecha, semana_medicion, semana_label,
       equipo, componente, ubicacion, usuario,
       horometro, mm_usada, condicion_pct, estado,
       tasa_mm_h, horas_a_critico, dias_a_critico,
       es_cambio
a:

SELECT id, fecha, semana_medicion, semana_label,
       equipo, componente, usuario,
       horometro, mm_usada, condicion_pct, estado,
       tasa_mm_h, horas_a_critico, dias_a_critico,
       es_cambio
7) Quita el mensaje temporal de Supabase
Borra esta línea:

st.write("Supabase OK:", supabase is not None)
Otras mejoras que sí haría ahora
Vi 3 cosas adicionales que conviene arreglar ya:

1. El caption final está desactualizado
Tu app dice todavía:
“Para producción migrar a Supabase”, pero ya empezaste la conexión a Supabase. Ese texto te va a confundir después. 


Cámbialo por algo como:

st.caption(
    "⚠️ Nota: El envío automático de correo los miércoles requiere Power Automate o programador externo."
)
2. El tab “Estado de flota” debería mostrar la fecha visible
Antes de st.dataframe(proy...), arma un display más útil:

cols_proj = [c for c in ["equipo", "fecha", "mm_usada", "estado", "tasa_mm_h", "horas_a_critico", "dias_a_critico"] if c in ultimos_flot.columns]
proy = ultimos_flot[cols_proj].copy()
3. El cambio de cuchilla también debería poder usar fecha manual
Hoy guardar_cambio_cuchilla() usa datetime.now(). Si el registro se carga después, te puede quedar corrida la trazabilidad. Conviene agregar también fecha de cambio visible en ese tab. 


Mi opinión
Sí, el cambio Ubicación → Fecha es correcto y mejora mucho la app.
Operacionalmente te aporta más porque:

amarra la medición al horómetro,

mejora el historial,

permite cruzar con Excel diario,

y deja mejor base para tasa de desgaste.

Lo siguiente más inteligente, después de esto, es:
agregar la fecha manual también al cambio de cuchilla y luego recién pasar el guardado completo a Supabase.

Si quieres, en el próximo mensaje te dejo el bloque completo ya reescrito del tab “Ingreso Medición” para copiar y pegar directo.


pero pasame el codigo completo

Sí. Te dejo el código completo ya modificado con estos cambios principales, basados en tu app.py actual: “Ubicación” fue reemplazada por “Fecha de medición”, la fecha ahora se guarda junto al horómetro, se muestra mejor en historial/estado, y saqué el st.write("Supabase OK...") temporal. También dejé el bloque de conexión Supabase, pero tu app todavía guarda en SQLite igual que antes; esa migración completa la hacemos después. 


Copia y reemplaza todo tu app.py por esto:

from __future__ import annotations

import io
import sqlite3
from dataclasses import dataclass
from datetime import datetime, date, timedelta, time
from typing import List, Tuple, Optional, Dict

import pandas as pd
import streamlit as st
from supabase import create_client


@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


# Conexión creada para futura migración de persistencia.
# Por ahora la app sigue guardando en SQLite.
supabase = get_supabase()


# ==============================
# ESTILO TECK
# ==============================

TECK_GREEN = "#007A3D"
TECK_GREEN_2 = "#00A04A"
TECK_DARK = "#0B0F14"


def inject_teck_style():
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: radial-gradient(1200px 800px at 10% 10%, #101826 0%, {TECK_DARK} 55%, #070A0E 100%);
        }}
        .block-container {{
            padding-top: 1.0rem !important;
            padding-bottom: 2.0rem !important;
        }}
        .teck-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 16px 20px;
            border-radius: 16px;
            background: linear-gradient(90deg, rgba(0,122,61,.28) 0%, rgba(0,160,74,.12) 45%, rgba(255,255,255,.03) 100%);
            border: 1px solid rgba(0,160,74,.35);
            box-shadow: 0 12px 30px rgba(0,0,0,.35);
            margin-bottom: 18px;
        }}
        .teck-badge {{
            padding: 8px 12px;
            border-radius: 999px;
            font-size: .85rem;
            font-weight: 800;
            color: white;
            background: linear-gradient(180deg, {TECK_GREEN_2} 0%, {TECK_GREEN} 100%);
            border: 1px solid rgba(255,255,255,.18);
            white-space: nowrap;
        }}
        .cambio-box {{
            background: rgba(0,122,61,.15);
            border: 1px solid rgba(0,160,74,.4);
            border-radius: 12px;
            padding: 14px 16px;
            margin-top: 10px;
        }}
        .cambio-badge {{
            display: inline-block;
            background: linear-gradient(90deg, #007A3D, #00A04A);
            color: white;
            font-weight: 800;
            font-size: .8rem;
            padding: 3px 10px;
            border-radius: 999px;
            margin-bottom: 8px;
        }}
        div.stButton > button {{
            border-radius: 12px !important;
            font-weight: 800 !important;
            border: 1px solid rgba(0,160,74,.35) !important;
        }}
        div.stButton > button[kind="primary"] {{
            background: linear-gradient(180deg, {TECK_GREEN_2} 0%, {TECK_GREEN} 100%) !important;
        }}
        [data-testid="stDataFrame"] {{
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,.08);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def render_header():
    st.markdown(
        f"""
        <div class="teck-header">
          <div>
            <p style="font-size:56px; font-weight:900; margin:0; line-height:1.05;">
              GET Wear Monitor
            </p>
            <p style="font-size:24px; margin:6px 0 0 0; opacity:.92;">
              Sistema de monitoreo y proyección de desgaste de cuchillas
            </p>
            <p style="font-size:16px; margin:10px 0 0 0; opacity:.82;">
              <b>Creado por:</b> Pablo Cortés Ramos · Ingeniero de Mantenimiento / Confiabilidad
            </p>
          </div>
          <div class="teck-badge">Teck QB2 · GET Wear Monitor</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==============================
# CONFIG
# ==============================

DB_PATH = "mediciones.db"

EQUIPOS = [
    "101", "102", "103", "104", "105", "106", "108",
    "201", "202", "203", "204", "205",
    "301", "302", "303",
]

EQUIPOS_MOTONIVELADORA = {"301", "302", "303"}

REF_WEEK_START = date(2026, 3, 5)
REF_WEEK_NUMBER = 10

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "")

REGLAS: Dict[str, dict] = {
    "MOTONIVELADORA": {
        "puntos": [
            (122, 100), (145, 91), (167, 78), (190, 65),
            (212, 52), (235, 39), (257, 26), (280, 13), (302, 0),
        ],
        "umbrales": [
            ("CRÍTICO", 90, "Cambiar cuchilla / condición inaceptable (rojo)."),
            ("MEDIO", 65, "Monitorear condición (amarillo)."),
            ("OK", 0, "Operación normal (verde)."),
        ],
        "mm_nuevo": 302.0,
        "mm_critico": 145.0,
        "label_pct": "Desgaste (%)",
    },
    "DOZER_854_D10_D11": {
        "puntos": [
            (75, 100), (82, 95), (83, 90), (100, 75),
            (140, 45), (170, 0),
        ],
        "umbrales": [
            ("CRÍTICO", 95, "Detención inmediata."),
            ("ALTO", 75, "Programar cambio."),
            ("MEDIO", 45, "Monitorear condición."),
            ("OK", 0, "Operación normal."),
        ],
        "mm_nuevo": 170.0,
        "mm_critico": 82.0,
        "label_pct": "Desgaste (%)",
    },
}

HORAS_POR_DIA = 24
N_TASA = 5


# ==============================
# MODELO
# ==============================

@dataclass
class Resultado:
    mm_izq: float
    mm_der: float
    mm_usada: float
    desgaste_pct: float
    estado: str
    accion: str
    horometro: float
    tasa_mm_h: Optional[float]
    horas_a_critico: Optional[float]
    dias_a_critico: Optional[float]
    regla: str


# ==============================
# SEMANA
# ==============================

def calcular_semana_medicion(fecha_dt: datetime) -> tuple[int, str, date, date]:
    week_offset = (fecha_dt.date() - REF_WEEK_START).days // 7
    semana = REF_WEEK_NUMBER + week_offset
    inicio = REF_WEEK_START + timedelta(days=week_offset * 7)
    fin = inicio + timedelta(days=6)
    etiqueta = f"Semana {semana}"
    return semana, etiqueta, inicio, fin


# ==============================
# DB — ESQUEMA AMPLIADO
# ==============================

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS mediciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            equipo TEXT NOT NULL,
            usuario TEXT,
            componente TEXT,
            mm REAL,
            horometro REAL,
            mm_izq REAL,
            mm_der REAL,
            mm_usada REAL,
            condicion_pct REAL,
            estado TEXT,
            accion TEXT,
            tasa_mm_h REAL,
            horas_a_critico REAL,
            dias_a_critico REAL,
            semana_medicion INTEGER,
            semana_label TEXT,
            inicio_semana TEXT,
            fin_semana TEXT,
            es_cambio INTEGER DEFAULT 0
        )
        """)

        con.execute("""
        CREATE TABLE IF NOT EXISTS cambios_cuchilla (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            equipo TEXT NOT NULL,
            horometro REAL NOT NULL,
            mm_izq_final REAL,
            mm_der_final REAL,
            fue_virada INTEGER DEFAULT 0,
            motivo TEXT,
            observaciones TEXT,
            tecnico_1 TEXT,
            tecnico_2 TEXT,
            usuario TEXT,
            semana_medicion INTEGER,
            semana_label TEXT
        )
        """)
        con.commit()


def migrar_db_agregar_columnas():
    with sqlite3.connect(DB_PATH) as con:
        cols = {row[1] for row in con.execute("PRAGMA table_info(mediciones)").fetchall()}
        faltantes = {
            "usuario": "usuario TEXT",
            "componente": "componente TEXT",
            "mm": "mm REAL",
            "horometro": "horometro REAL",
            "mm_izq": "mm_izq REAL",
            "mm_der": "mm_der REAL",
            "mm_usada": "mm_usada REAL",
            "condicion_pct": "condicion_pct REAL",
            "estado": "estado TEXT",
            "accion": "accion TEXT",
            "tasa_mm_h": "tasa_mm_h REAL",
            "horas_a_critico": "horas_a_critico REAL",
            "dias_a_critico": "dias_a_critico REAL",
            "semana_medicion": "semana_medicion INTEGER",
            "semana_label": "semana_label TEXT",
            "inicio_semana": "inicio_semana TEXT",
            "fin_semana": "fin_semana TEXT",
            "es_cambio": "es_cambio INTEGER DEFAULT 0",
        }
        for col, ddl in faltantes.items():
            if col not in cols:
                con.execute(f"ALTER TABLE mediciones ADD COLUMN {ddl}")
        con.commit()


def guardar_medicion(
    fecha_medicion: date,
    equipo: str,
    usuario: str,
    horometro: float,
    mm_izq: float,
    mm_der: float,
    mm_usada: float,
    desgaste_pct: float,
    estado: str,
    accion: str,
    tasa_mm_h: Optional[float],
    horas_a_critico: Optional[float],
    dias_a_critico: Optional[float],
):
    fecha_dt = datetime.combine(fecha_medicion, time(12, 0))
    semana, semana_label, ini_sem, fin_sem = calcular_semana_medicion(fecha_dt)

    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            INSERT INTO mediciones (
                fecha, equipo, usuario, componente, mm,
                horometro, mm_izq, mm_der, mm_usada,
                condicion_pct, estado, accion,
                tasa_mm_h, horas_a_critico, dias_a_critico,
                semana_medicion, semana_label, inicio_semana, fin_semana,
                es_cambio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            fecha_dt.isoformat(timespec="seconds"),
            equipo,
            (usuario or "").strip() or None,
            "Cuchilla",
            float(mm_usada),
            float(horometro),
            float(mm_izq),
            float(mm_der),
            float(mm_usada),
            float(desgaste_pct),
            estado,
            accion,
            float(tasa_mm_h) if tasa_mm_h is not None else None,
            float(horas_a_critico) if horas_a_critico is not None else None,
            float(dias_a_critico) if dias_a_critico is not None else None,
            int(semana),
            semana_label,
            ini_sem.isoformat(),
            fin_sem.isoformat(),
        ))
        con.commit()


def guardar_cambio_cuchilla(
    fecha_cambio: date,
    equipo: str,
    horometro: float,
    mm_izq_final: float,
    mm_der_final: float,
    fue_virada: bool,
    motivo: str,
    observaciones: str,
    tecnico_1: str,
    tecnico_2: str,
    usuario: str,
):
    fecha_dt = datetime.combine(fecha_cambio, time(12, 0))
    semana, semana_label, _, _ = calcular_semana_medicion(fecha_dt)

    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            INSERT INTO cambios_cuchilla (
                fecha, equipo, horometro, mm_izq_final, mm_der_final,
                fue_virada, motivo, observaciones,
                tecnico_1, tecnico_2, usuario,
                semana_medicion, semana_label
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fecha_dt.isoformat(timespec="seconds"),
            equipo, float(horometro),
            float(mm_izq_final), float(mm_der_final),
            1 if fue_virada else 0,
            motivo, observaciones,
            (tecnico_1 or "").strip() or None,
            (tecnico_2 or "").strip() or None,
            (usuario or "").strip() or None,
            int(semana), semana_label,
        ))

        regla = regla_por_equipo(equipo)
        cfg = REGLAS[regla]
        mm_nuevo = cfg["mm_nuevo"]

        con.execute("""
            INSERT INTO mediciones (
                fecha, equipo, usuario, componente, mm,
                horometro, mm_izq, mm_der, mm_usada,
                condicion_pct, estado, accion,
                semana_medicion, semana_label, es_cambio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            fecha_dt.isoformat(timespec="seconds"),
            equipo,
            (tecnico_1 or usuario or "").strip() or None,
            "Cuchilla NUEVA",
            mm_nuevo, float(horometro),
            mm_nuevo, mm_nuevo, mm_nuevo,
            0.0, "OK", "GET nuevo instalado — iniciar monitoreo.",
            int(semana), semana_label,
        ))
        con.commit()


@st.cache_data(ttl=60)
def cargar_historial(limit: int = 500) -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as con:
        df = pd.read_sql_query(f"""
            SELECT id, fecha, semana_medicion, semana_label,
                   equipo, componente, usuario,
                   horometro, mm_usada, condicion_pct, estado,
                   tasa_mm_h, horas_a_critico, dias_a_critico,
                   es_cambio
            FROM mediciones
            WHERE semana_medicion IS NOT NULL
            ORDER BY datetime(fecha) DESC
            LIMIT {int(limit)}
        """, con)
    return df.loc[:, ~df.columns.duplicated()]


@st.cache_data(ttl=60)
def cargar_cambios() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as con:
        df = pd.read_sql_query("""
            SELECT id, fecha, equipo, horometro,
                   mm_izq_final, mm_der_final,
                   fue_virada, motivo, observaciones,
                   tecnico_1, tecnico_2, usuario,
                   semana_label
            FROM cambios_cuchilla
            ORDER BY datetime(fecha) DESC
        """, con)
    return df


def obtener_ultimo_cambio_equipo(equipo: str) -> Optional[dict]:
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
            SELECT fecha, horometro FROM cambios_cuchilla
            WHERE equipo = ?
            ORDER BY datetime(fecha) DESC LIMIT 1
        """, (equipo,))
        row = cur.fetchone()
    if row:
        return {"fecha": row[0], "horometro": float(row[1])}
    return None


def obtener_ultimas_mediciones_equipo(equipo: str, n: int = N_TASA) -> list[dict]:
    ultimo = obtener_ultimo_cambio_equipo(equipo)
    fecha_desde = ultimo["fecha"] if ultimo else "2000-01-01"

    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
            SELECT horometro, mm_usada
            FROM mediciones
            WHERE equipo = ?
              AND horometro IS NOT NULL
              AND mm_usada IS NOT NULL
              AND es_cambio = 0
              AND datetime(fecha) >= datetime(?)
            ORDER BY datetime(fecha) DESC
            LIMIT ?
        """, (equipo, fecha_desde, n))
        rows = cur.fetchall()
    return [{"horometro": float(h), "mm_usada": float(mm)} for h, mm in rows]


def eliminar_mediciones_por_ids(ids: list[int]) -> int:
    if not ids:
        return 0
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.executemany("DELETE FROM mediciones WHERE id = ?", [(int(i),) for i in ids])
        con.commit()
        return cur.rowcount


def eliminar_registros_prueba() -> int:
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute("""
            DELETE FROM mediciones
            WHERE usuario IS NULL
               OR TRIM(usuario) = ''
               OR LOWER(TRIM(usuario)) IN (
                   'prueba','test','demo','usuario prueba',
                   'pajarraco medidor','cristian olivares'
               )
               OR semana_medicion IS NULL
        """)
        con.commit()
        return cur.rowcount


# ==============================
# CÁLCULO
# ==============================

def regla_por_equipo(equipo: str) -> str:
    return "MOTONIVELADORA" if equipo in EQUIPOS_MOTONIVELADORA else "DOZER_854_D10_D11"


def rango_regla(regla: str) -> tuple[float, float]:
    puntos = REGLAS[regla]["puntos"]
    xs = [p[0] for p in puntos]
    return min(xs), max(xs)


def interpolar_pct(mm: float, puntos: List[Tuple[float, float]]) -> float:
    puntos = sorted(puntos, key=lambda x: x[0])
    if mm <= puntos[0][0]:
        return float(puntos[0][1])
    if mm >= puntos[-1][0]:
        return float(puntos[-1][1])
    for (x1, y1), (x2, y2) in zip(puntos[:-1], puntos[1:]):
        if x1 <= mm <= x2:
            t = (mm - x1) / (x2 - x1)
            return float(y1 + t * (y2 - y1))
    return float(puntos[-1][1])


def clasificar_desgaste(desgaste_pct: float, umbrales) -> tuple[str, str]:
    for estado, limite, accion in umbrales:
        if desgaste_pct >= limite:
            return estado, accion
    return "OK", "Operación normal."


def calcular_tasa_mm_h_promedio(meds: list[dict]) -> Optional[float]:
    if len(meds) < 2:
        return None
    tasas = []
    for i in range(len(meds) - 1):
        h_new, mm_new = meds[i]["horometro"], meds[i]["mm_usada"]
        h_old, mm_old = meds[i + 1]["horometro"], meds[i + 1]["mm_usada"]
        dh = h_new - h_old
        dmm = mm_old - mm_new
        if dh > 0 and dmm > 0:
            tasas.append(dmm / dh)
    if not tasas:
        return None
    return sum(tasas) / len(tasas)


def proyectar_a_critico(mm_usada, tasa_mm_h, mm_critico) -> tuple[Optional[float], Optional[float]]:
    if tasa_mm_h is None or tasa_mm_h <= 0:
        return None, None
    restante_mm = mm_usada - mm_critico
    if restante_mm <= 0:
        return 0.0, 0.0
    horas = restante_mm / tasa_mm_h
    dias = horas / HORAS_POR_DIA
    return round(horas, 1), round(dias, 1)


def evaluar(equipo: str, horometro: float, mm_izq: float, mm_der: float) -> Resultado:
    mm_usada = min(mm_izq, mm_der)
    regla = regla_por_equipo(equipo)
    cfg = REGLAS[regla]
    desgaste = float(interpolar_pct(mm_usada, cfg["puntos"]))
    estado, accion = clasificar_desgaste(desgaste, cfg["umbrales"])
    meds = [{"horometro": float(horometro), "mm_usada": float(mm_usada)}] + \
           obtener_ultimas_mediciones_equipo(equipo, n=N_TASA)
    tasa_mm_h = calcular_tasa_mm_h_promedio(meds)
    horas_a_critico, dias_a_critico = proyectar_a_critico(mm_usada, tasa_mm_h, cfg["mm_critico"])
    return Resultado(
        mm_izq=mm_izq, mm_der=mm_der, mm_usada=mm_usada,
        desgaste_pct=round(desgaste, 1), estado=estado, accion=accion,
        horometro=horometro,
        tasa_mm_h=round(tasa_mm_h, 4) if tasa_mm_h is not None else None,
        horas_a_critico=horas_a_critico, dias_a_critico=dias_a_critico,
        regla=regla,
    )


# ==============================
# REPORTES / KPI
# ==============================

def ultimos_estados_por_equipo(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df2 = df.copy()
    df2["fecha_dt"] = pd.to_datetime(df2["fecha"], errors="coerce")
    df2 = df2.sort_values("fecha_dt", ascending=False)
    return df2.drop_duplicates(subset=["equipo"], keep="first")


def generar_excel_bytes(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="ReporteSemanal")
    return output.getvalue()


def generar_resumen_mail(df: pd.DataFrame) -> str:
    if df.empty:
        return "Sin datos para el reporte semanal."
    ec = df["estado"].value_counts()
    return f"""Reporte semanal GET Wear Monitor
OK: {int(ec.get("OK", 0))}
Monitoreo: {int(ec.get("MEDIO", 0))}
Programar cambio: {int(ec.get("ALTO", 0))}
Crítico: {int(ec.get("CRÍTICO", 0))}""".strip()


# ==============================
# UI PRINCIPAL
# ==============================

st.set_page_config(page_title="Teck · GET Wear Monitor", layout="wide")
inject_teck_style()
init_db()
migrar_db_agregar_columnas()
render_header()

with st.sidebar:
    st.subheader("Administración")
    admin_ok = False
    if ADMIN_PASSWORD:
        pwd = st.text_input("Clave administrador", type="password")
        admin_ok = (pwd == ADMIN_PASSWORD)
        if admin_ok:
            st.success("Modo administrador activo")
    else:
        st.info("Define ADMIN_PASSWORD en Secrets.")

tab_medicion, tab_cambio, tab_historial, tab_cambios, tab_flota, tab_reporte = st.tabs([
    "📏 Ingreso Medición",
    "🔄 Cambio de Cuchilla",
    "📋 Historial",
    "🔧 Registro de Cambios",
    "🚛 Estado Flota",
    "📊 Reporte Semanal",
])

# ─────────────────────────────────────────────
# TAB 1: INGRESO DE MEDICIÓN
# ─────────────────────────────────────────────
with tab_medicion:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("Ingreso de medición")

        equipo = st.selectbox("Equipo", EQUIPOS, index=0, key="eq_med")
        fecha_medicion = st.date_input("Fecha de medición", value=date.today(), key="fc_med")
        usuario = st.text_input("Usuario (Técnico)", value="", key="us_med")

        st.divider()

        horometro = st.number_input("Horómetro", min_value=0.0, value=0.0, step=1.0, key="hr_med")

        regla_actual = regla_por_equipo(equipo)
        mm_max = REGLAS[regla_actual]["mm_nuevo"]

        mm_izq = st.number_input(
            "Medición Izquierda (mm)",
            min_value=0.0, value=mm_max, step=0.1, format="%.2f", key="mi_med"
        )
        mm_der = st.number_input(
            "Medición Derecha (mm)",
            min_value=0.0, value=mm_max, step=0.1, format="%.2f", key="md_med"
        )

        st.caption("Se usa automáticamente el valor MENOR (más crítico) para evaluar y proyectar.")

        ultimo_cambio = obtener_ultimo_cambio_equipo(equipo)
        if ultimo_cambio:
            st.info(
                f"📌 Último cambio de cuchilla: {ultimo_cambio['fecha'][:10]} · "
                f"Horómetro: {ultimo_cambio['horometro']:,.0f} hrs"
            )
        else:
            st.caption("ℹ️ Sin cambio de cuchilla registrado. La tasa usa todo el historial.")

        if st.button("Evaluar y guardar", type="primary", key="btn_med"):
            if not usuario.strip():
                st.error("Debes ingresar el nombre del técnico.")
            elif horometro <= 0:
                st.error("Debes ingresar un horómetro válido (> 0).")
            else:
                regla = regla_por_equipo(equipo)
                mm_min_val, mm_max_val = rango_regla(regla)
                errores = []
                if not (mm_min_val <= mm_izq <= mm_max_val):
                    errores.append(f"Medición izquierda fuera de rango ({mm_min_val}–{mm_max_val} mm).")
                if not (mm_min_val <= mm_der <= mm_max_val):
                    errores.append(f"Medición derecha fuera de rango ({mm_min_val}–{mm_max_val} mm).")

                if errores:
                    for e in errores:
                        st.error(e)
                    st.stop()

                res = evaluar(equipo, horometro, mm_izq, mm_der)
                cfg = REGLAS[res.regla]
                semana, semana_label, ini_sem, fin_sem = calcular_semana_medicion(
                    datetime.combine(fecha_medicion, time(12, 0))
                )

                guardar_medicion(
                    fecha_medicion=fecha_medicion,
                    equipo=equipo,
                    usuario=usuario,
                    horometro=res.horometro,
                    mm_izq=res.mm_izq,
                    mm_der=res.mm_der,
                    mm_usada=res.mm_usada,
                    desgaste_pct=res.desgaste_pct,
                    estado=res.estado,
                    accion=res.accion,
                    tasa_mm_h=res.tasa_mm_h,
                    horas_a_critico=res.horas_a_critico,
                    dias_a_critico=res.dias_a_critico,
                )
                cargar_historial.clear()

                color_estado = {"OK": "🟢", "MEDIO": "🟡", "ALTO": "🟠", "CRÍTICO": "🔴"}.get(res.estado, "⚪")
                st.success(f"✅ Medición guardada · {semana_label} ({ini_sem} → {fin_sem})")
                st.metric("Mm usada (menor)", f"{res.mm_usada:.2f}")
                st.metric(cfg["label_pct"], f"{res.desgaste_pct:.1f}%")
                st.metric("Estado", f"{color_estado} {res.estado}")
                st.write("**Acción recomendada:**", res.accion)

                if res.tasa_mm_h is None:
                    st.info("Tasa mm/h: sin datos suficientes (mínimo 2 mediciones en el ciclo actual).")
                else:
                    st.info(f"Tasa estimada: **{res.tasa_mm_h} mm/h**")

                if res.horas_a_critico is None:
                    st.warning("Proyección a crítico: no disponible (se necesita tasa calculada).")
                else:
                    st.warning(
                        f"⏱ Proyección a crítico (≤{cfg['mm_critico']} mm): "
                        f"~**{res.horas_a_critico} h** (~**{res.dias_a_critico} días**)"
                    )

    with col2:
        st.subheader("Historial de Mediciones")
        df_hist = cargar_historial(limit=500)
        if not df_hist.empty:
            df_eq = df_hist[df_hist["equipo"] == equipo].head(20).copy()
            if not df_eq.empty:
                df_eq["fecha"] = pd.to_datetime(df_eq["fecha"], errors="coerce").dt.strftime("%Y-%m-%d")
                st.dataframe(df_eq.drop(columns=["id"], errors="ignore"), use_container_width=True)
            else:
                st.info(f"Sin mediciones para equipo {equipo}.")
        else:
            st.info("Sin mediciones aún.")


# ─────────────────────────────────────────────
# TAB 2: CAMBIO DE CUCHILLA
# ─────────────────────────────────────────────
with tab_cambio:
    st.subheader("🔄 Registro de Cambio de Cuchilla / GET")
    st.caption(
        "Completa este formulario al instalar un GET nuevo. "
        "Se registrará la medición final de la cuchilla retirada y se iniciará un ciclo de desgaste nuevo."
    )

    c1, c2 = st.columns([1, 1], gap="large")

    with c1:
        st.markdown("#### Datos del equipo")
        eq_cambio = st.selectbox("Equipo", EQUIPOS, key="eq_cambio")
        fecha_cambio = st.date_input("Fecha de cambio", value=date.today(), key="fc_cambio")
        hr_cambio = st.number_input("Horómetro al momento del cambio", min_value=0.0, value=0.0, step=1.0, key="hr_cambio")

        regla_cambio = regla_por_equipo(eq_cambio)
        mm_max_cambio = REGLAS[regla_cambio]["mm_nuevo"]
        mm_critico_cambio = REGLAS[regla_cambio]["mm_critico"]

        st.markdown("#### Medición final del GET retirado")
        mm_izq_final = st.number_input(
            "Altura cuchilla IZQUIERDA al retiro (mm)",
            min_value=0.0, max_value=float(mm_max_cambio),
            value=float(mm_critico_cambio), step=0.1, format="%.1f",
            key="mi_cambio"
        )
        mm_der_final = st.number_input(
            "Altura cuchilla DERECHA al retiro (mm)",
            min_value=0.0, max_value=float(mm_max_cambio),
            value=float(mm_critico_cambio), step=0.1, format="%.1f",
            key="md_cambio"
        )

        fue_virada = st.radio(
            "¿La cuchilla fue virada antes del cambio?",
            options=["NO", "SÍ"],
            horizontal=True,
            key="virada_cambio"
        )

        motivo = st.selectbox(
            "Motivo del cambio",
            options=[
                "Desgaste normal (límite alcanzado)",
                "Cambio preventivo (programado)",
                "Daño / impacto",
                "Cambio por campaña de mantenimiento",
                "Otro",
            ],
            key="motivo_cambio"
        )

    with c2:
        st.markdown("#### Técnicos participantes")
        tecnico_1 = st.text_input("Técnico 1 (nombre y apellido)", key="tec1_cambio")
        tecnico_2 = st.text_input("Técnico 2 (nombre y apellido, opcional)", key="tec2_cambio")

        st.markdown("#### Observaciones generales")
        observaciones = st.text_area(
            "OT generadas / actividades adicionales / aspectos de seguridad / anomalías",
            height=120,
            key="obs_cambio"
        )

        st.markdown("#### Autorización")
        supervisor = st.text_input("Usuario que registra (supervisor / técnico líder)", key="sup_cambio")

        st.divider()

        st.markdown("**ℹ️ Al confirmar el cambio:**")
        st.markdown(
            f"- Se registrará la medición final del GET retirado\n"
            f"- Se iniciará ciclo nuevo con **{mm_max_cambio:.0f} mm** (GET nuevo)\n"
            f"- La tasa de desgaste se calculará desde este horómetro en adelante"
        )

        if st.button("✅ Confirmar cambio de cuchilla", type="primary", key="btn_cambio"):
            errores = []
            if hr_cambio <= 0:
                errores.append("Horómetro debe ser mayor que 0.")
            if not tecnico_1.strip():
                errores.append("Debe ingresar al menos el Técnico 1.")
            if not supervisor.strip():
                errores.append("Debe ingresar el usuario que registra.")

            if errores:
                for e in errores:
                    st.error(e)
            else:
                guardar_cambio_cuchilla(
                    fecha_cambio=fecha_cambio,
                    equipo=eq_cambio,
                    horometro=hr_cambio,
                    mm_izq_final=mm_izq_final,
                    mm_der_final=mm_der_final,
                    fue_virada=(fue_virada == "SÍ"),
                    motivo=motivo,
                    observaciones=observaciones,
                    tecnico_1=tecnico_1,
                    tecnico_2=tecnico_2,
                    usuario=supervisor,
                )
                cargar_historial.clear()
                cargar_cambios.clear()

                st.success(
                    f"🔄 Cambio de cuchilla registrado para Equipo **{eq_cambio}** "
                    f"· Fecha: **{fecha_cambio}** · Horómetro: **{hr_cambio:,.0f} hrs**\n\n"
                    f"Ciclo nuevo iniciado con GET de **{mm_max_cambio:.0f} mm**."
                )
                st.balloons()


# ─────────────────────────────────────────────
# TAB 3: HISTORIAL COMPLETO
# ─────────────────────────────────────────────
with tab_historial:
    st.subheader("Historial de Mediciones")
    df_h = cargar_historial(limit=500)

    if not df_h.empty:
        fc1, fc2 = st.columns(2)
        with fc1:
            eq_filtro = st.multiselect("Filtrar por equipo", options=sorted(df_h["equipo"].unique()), default=[])
        with fc2:
            estado_filtro = st.multiselect("Filtrar por estado", options=sorted(df_h["estado"].dropna().unique()), default=[])

        df_show = df_h.copy()
        if eq_filtro:
            df_show = df_show[df_show["equipo"].isin(eq_filtro)]
        if estado_filtro:
            df_show = df_show[df_show["estado"].isin(estado_filtro)]

        df_show["fecha"] = pd.to_datetime(df_show["fecha"], errors="coerce").dt.strftime("%Y-%m-%d")

        columnas_hist = [
            c for c in [
                "fecha", "semana_label", "equipo", "componente", "usuario",
                "horometro", "mm_usada", "condicion_pct", "estado",
                "tasa_mm_h", "horas_a_critico", "dias_a_critico", "es_cambio"
            ] if c in df_show.columns
        ]
        st.dataframe(df_show[columnas_hist], use_container_width=True)

        if admin_ok and "id" in df_h.columns:
            st.markdown("### Eliminar registro")
            df_del = df_h[["id", "fecha", "equipo", "usuario", "estado"]].copy()
            df_del["desc"] = df_del.apply(
                lambda r: f"ID {int(r['id'])} | {r['fecha']} | Eq {r['equipo']} | {r['usuario']} | {r['estado']}", axis=1
            )
            sel = st.selectbox("Seleccionar registro", [""] + df_del["desc"].tolist())
            if sel:
                id_borrar = int(sel.split("|")[0].replace("ID", "").strip())
                if st.button("Eliminar registro seleccionado", type="primary"):
                    n = eliminar_mediciones_por_ids([id_borrar])
                    st.success(f"Se eliminaron {n} medición(es).")
                    cargar_historial.clear()
                    st.rerun()
    else:
        st.info("Sin mediciones aún.")


# ─────────────────────────────────────────────
# TAB 4: REGISTRO DE CAMBIOS
# ─────────────────────────────────────────────
with tab_cambios:
    st.subheader("🔧 Historial de Cambios de Cuchilla")
    df_cambios = cargar_cambios()

    if not df_cambios.empty:
        df_display = df_cambios.copy()
        df_display["fue_virada"] = df_display["fue_virada"].map({1: "SÍ", 0: "NO"})
        df_display["fecha"] = pd.to_datetime(df_display["fecha"], errors="coerce").dt.strftime("%Y-%m-%d")
        df_display = df_display.rename(columns={
            "fecha": "Fecha",
            "equipo": "Equipo",
            "horometro": "Horómetro",
            "mm_izq_final": "IZQ final (mm)",
            "mm_der_final": "DER final (mm)",
            "fue_virada": "Fue virada",
            "motivo": "Motivo",
            "observaciones": "Observaciones",
            "tecnico_1": "Técnico 1",
            "tecnico_2": "Técnico 2",
            "usuario": "Registrado por",
            "semana_label": "Semana",
        })
        st.dataframe(
            df_display.drop(columns=["id"], errors="ignore"),
            use_container_width=True
        )

        st.divider()
        st.markdown("#### Resumen por equipo")
        resumen = df_cambios.groupby("equipo").agg(
            total_cambios=("id", "count"),
            ultimo_cambio=("fecha", "max"),
            ultimo_horometro=("horometro", "max"),
        ).reset_index()
        st.dataframe(resumen, use_container_width=True)

        st.download_button(
            "⬇️ Descargar historial de cambios Excel",
            data=generar_excel_bytes(df_display.drop(columns=["id"], errors="ignore")),
            file_name="cambios_cuchilla.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Sin cambios de cuchilla registrados aún.")


# ─────────────────────────────────────────────
# TAB 5: ESTADO DE FLOTA
# ─────────────────────────────────────────────
with tab_flota:
    st.subheader("Estado de flota")
    df_flot = cargar_historial(limit=5000)
    ultimos_flot = ultimos_estados_por_equipo(df_flot) if not df_flot.empty else pd.DataFrame()

    if not ultimos_flot.empty:
        ultimos_flot["fecha"] = pd.to_datetime(ultimos_flot["fecha"], errors="coerce").dt.strftime("%Y-%m-%d")

        ec = ultimos_flot["estado"].value_counts()
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🟢 OK", int(ec.get("OK", 0)))
        k2.metric("🟡 Monitoreo", int(ec.get("MEDIO", 0)))
        k3.metric("🟠 Programar cambio", int(ec.get("ALTO", 0)))
        k4.metric("🔴 Crítico", int(ec.get("CRÍTICO", 0)))

        st.divider()
        st.subheader("Ranking de desgaste por equipo")
        if "condicion_pct" in ultimos_flot.columns:
            ranking = ultimos_flot[["equipo", "condicion_pct"]].copy()
            ranking = ranking.sort_values("condicion_pct", ascending=False)
            ranking = ranking.rename(columns={"condicion_pct": "desgaste_pct"})
            st.bar_chart(ranking.set_index("equipo"))
            st.dataframe(ranking, use_container_width=True)

        st.divider()
        st.subheader("Proyección de cambio")
        cols_proj = [
            c for c in ["equipo", "fecha", "mm_usada", "estado", "tasa_mm_h", "horas_a_critico", "dias_a_critico"]
            if c in ultimos_flot.columns
        ]
        proy = ultimos_flot[cols_proj].copy()
        if "horas_a_critico" in proy.columns:
            proy = proy.sort_values("horas_a_critico", na_position="last")
        st.dataframe(proy, use_container_width=True)
    else:
        st.info("Sin datos para estado de flota.")


# ─────────────────────────────────────────────
# TAB 6: REPORTE SEMANAL
# ─────────────────────────────────────────────
with tab_reporte:
    st.subheader("Reporte semanal")
    df_all = cargar_historial(limit=5000)

    if not df_all.empty and "semana_medicion" in df_all.columns:
        semanas_disp = sorted(df_all["semana_medicion"].dropna().astype(int).unique().tolist(), reverse=True)
        if semanas_disp:
            semana_sel = st.selectbox("Semana a reportar", semanas_disp)
            eq_disp = ["TODOS"] + sorted(df_all["equipo"].dropna().astype(str).unique().tolist())
            eq_sel = st.selectbox("Equipo", eq_disp)

            df_sem = df_all[df_all["semana_medicion"] == semana_sel].copy()
            if eq_sel != "TODOS":
                df_sem = df_sem[df_sem["equipo"].astype(str) == eq_sel].copy()

            df_rep = df_sem.copy()
            df_rep["criticidad"] = df_rep["condicion_pct"]
            cols_rep = ["fecha", "equipo", "semana_medicion", "usuario", "horometro", "criticidad", "estado"]
            cols_rep = [c for c in cols_rep if c in df_rep.columns]
            df_rep = df_rep[cols_rep]

            st.download_button(
                "⬇️ Descargar reporte semanal Excel",
                data=generar_excel_bytes(df_rep),
                file_name=f"reporte_semana_{semana_sel}_{eq_sel}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.text_area(
                "Resumen para correo",
                value=generar_resumen_mail(ultimos_estados_por_equipo(df_sem)),
                height=150
            )
        else:
            st.info("No hay semanas válidas para reportar.")
    else:
        st.info("Sin datos suficientes para reporte semanal.")

    st.divider()
    st.subheader("Administración de datos")
    if admin_ok:
        with open(DB_PATH, "rb") as f:
            st.download_button(
                "⬇️ Descargar base de datos SQLite",
                data=f.read(),
                file_name="mediciones.db",
                mime="application/octet-stream"
            )
        if st.button("🗑️ Eliminar registros de prueba"):
            n = eliminar_registros_prueba()
            st.success(f"Se eliminaron {n} registros de prueba.")
            cargar_historial.clear()
            st.rerun()
    else:
        st.info("Descarga de base y eliminaciones solo para administrador.")


st.caption(
    "⚠️ Nota: El envío automático de correo los miércoles requiere Power Automate o programador externo."
)
