# Índice de Archivos - Agentes LangChain REACT

Este documento describe los objetivos y diferencias entre las diferentes versiones de agentes REACT implementadas en este proyecto.

## Resumen Ejecutivo

El proyecto evoluciona desde una implementación básica de agente REACT hasta versiones más complejas con múltiples herramientas, búsqueda web y interfaces gráficas. Todos los archivos comparten la misma arquitectura base: agente REACT con parsing manual de acciones y observaciones.

---

## Archivos por Orden de Evolución

### 1. `agente_react_01.py`
**Objetivo:** Implementación base del agente REACT con una única herramienta simple.

**Características:**
- **Tools:** `get_text_length` únicamente
- **Interfaz:** Consola (script ejecutable una vez)
- **Input:** Hardcodeado: "Cual es la longitud de la palabra: CYBERSEGURIDAD"
- **Parsing:** Básico, sin manejo especial de tipos
- **Documentación:** Herramientas con documentación estructurada (Description, Input, Output, Example)
- **Idioma:** Mensajes en español

**Uso:** Punto de partida para entender la estructura básica de un agente REACT.

---

### 2. `agente_react_02.py`
**Objetivo:** Extender el agente con herramientas que requieren múltiples parámetros.

**Características:**
- **Tools:** `get_text_length`, `multiplica2`
- **Interfaz:** Consola (script ejecutable una vez)
- **Input:** Hardcodeado (última línea activa: "Cuanto es 3.14 multiplicado por 4?")
- **Parsing:** Implementa `ast.literal_eval()` para parsear tuplas de parámetros
- **Mejora clave:** Resuelve el problema de pasar múltiples argumentos a herramientas
- **Documentación:** Herramientas con documentación estructurada mejorada
- **Idioma:** Inputs y mensajes en español

**Diferencias respecto a `agente_react_01.py`:**
- Agrega tool `multiplica2` que requiere dos parámetros
- Implementa parsing de tuplas con `ast.literal_eval()`
- Manejo de unpacking de tuplas: `tool_to_use.func(*tool_input_parsed)`

---

### 3. `agente_react_03.py`
**Objetivo:** Generalizar operaciones matemáticas con una herramienta de evaluación de expresiones.

**Características:**
- **Tools:** `get_text_length`, `multiplica2`, `math_operation`
- **Interfaz:** Consola (script ejecutable una vez)
- **Input:** Hardcodeado: "Please, calculate the following expression: 3 * 56.9 / 3"
- **Parsing:** Diferenciado por tipo de tool:
  - `multiplica2`: parsing de tupla con `eval()`
  - `math_operation`: limpieza de string y validación con regex
  - `get_text_length`: parsing directo
- **Validación:** Regex para validar expresiones matemáticas antes de evaluar
- **Documentación:** Herramientas con documentación estructurada mejorada
- **Idioma:** Mensajes en español

**Diferencias respecto a `agente_react_02.py`:**
- Agrega tool `math_operation` para evaluar expresiones matemáticas arbitrarias
- Implementa validación de seguridad con regex antes de usar `eval()`
- Parsing diferenciado según el tipo de herramienta

---

### 4. `agente_react_04.py`
**Objetivo:** Integrar búsqueda web mediante Tavily para ampliar capacidades del agente.

**Características:**
- **Tools:** `get_text_length`, `multiplica2`, `math_operation`, `web_search_tool` (Tavily)
- **Interfaz:** Consola (script ejecutable una vez)
- **Input:** Hardcodeado: "Cual ha sido el ultimo resultado del Atletico de Madrid y FC Barcelona en la temporada 2025?"
- **Parsing:** Extiende el parsing diferenciado para incluir Tavily
- **Búsqueda web:** Integración con `TavilySearchResults` (k=3 resultados)
- **Manejo de errores:** Try-except para capturar fallos en ejecución de tools
- **Fallback:** Búsqueda web automática si el agente no puede responder
- **Documentación:** Herramientas con documentación estructurada mejorada

**Diferencias respecto a `agente_react_03.py`:**
- Agrega integración con Tavily para búsqueda web
- Implementa manejo de excepciones con try-except
- Agrega lógica de fallback a búsqueda web
- Parsing especial para `tavily_search_results_json` usando `.run()` en lugar de `.func()`

---

### 5. `agente_react_05_CLI.py`
**Objetivo:** Crear una versión interactiva por consola para uso continuo.

**Características:**
- **Tools:** `get_text_length`, `multiplica2`, `math_operation`, `web_search_tool` (Tavily)
- **Interfaz:** Consola interactiva con loop `while True`
- **Input:** Entrada del usuario mediante `input()` en cada iteración
- **Salida:** Comando "END" para terminar la sesión
- **Logging:** Muestra información de depuración (longitud de pasos intermedios)
- **Parsing:** Mismo sistema diferenciado que `agente_react_04.py`
- **Idioma:** Interfaz completamente en español
- **Documentación:** Herramientas con documentación estructurada mejorada

**Diferencias respecto a `agente_react_04.py`:**
- Cambia de ejecución única a loop interactivo
- Permite múltiples consultas en la misma sesión
- Agrega comando de salida "END"
- Mejora el logging de depuración
- Interfaz y mensajes traducidos al español

---

### 6. `agente_react_06_streamlit.py`
**Objetivo:** Migrar la interfaz a Streamlit para una experiencia web interactiva.

**Características:**
- **Tools:** `get_text_length`, `multiplica2`, `math_operation`, `web_search_tool` (Tavily)
- **Interfaz:** Web UI con Streamlit
- **Input:** Campo de texto en la interfaz web
- **Historial:** Almacena conversación en `st.session_state["messages"]`
- **UI:** Interfaz moderna con spinner de carga y visualización de historial
- **Parsing:** Mismo sistema diferenciado que versiones anteriores
- **Memoria:** No implementa memoria conversacional (solo historial visual)
- **Idioma:** Interfaz completamente en español ("Chat con un Agente de IA!", "Su pregunta:", "Tu:", "Agente:")
- **Documentación:** Herramientas con documentación estructurada mejorada

**Diferencias respecto a `agente_react_05_CLI.py`:**
- Cambia de consola a interfaz web con Streamlit
- Almacena historial de conversación en session state
- Interfaz visual moderna con spinner y formato de chat
- No requiere comando "END" (sesión web continua)
- **Limitación:** No mantiene contexto entre consultas (sin memoria real)
- Interfaz traducida al español

---

### 7. `agente_react_07_memory.py`
**Objetivo:** Agregar memoria conversacional al agente Streamlit.

**Características:**
- **Tools:** `get_text_length`, `multiplica2`, `math_operation`, `web_search_tool` (Tavily)
- **Interfaz:** Web UI con Streamlit
- **Input:** Campo de texto en la interfaz web
- **Historial:** Almacena conversación en `st.session_state["messages"]`
- **Memoria:** Implementa `ConversationBufferMemory` correctamente inicializada y funcional
- **Template:** Incluye placeholder `{chat_history}` en el prompt para contexto conversacional
- **Modularización:** Importa herramientas desde `mis_tools.py` para mejor organización del código
- **Idioma:** Interfaz completamente en español
- **Debug:** Incluye expander para inspeccionar el contenido de la memoria

**Diferencias respecto a `agente_react_06_streamlit.py`:**
- Implementa `ConversationBufferMemory` de LangChain correctamente inicializada
- Template del prompt incluye sección de historial de chat para mantener contexto
- Agrega campo `chat_history` en el pipeline del agente
- El agente recuerda conversaciones anteriores y puede hacer referencia a mensajes previos
- Herramientas centralizadas en `mis_tools.py` para reutilización
- **Mejora:** Memoria completamente funcional y lista para producción

---

## Tabla Comparativa de Herramientas

| Archivo | get_text_length | multiplica2 | math_operation | Tavily Search | Interfaz | Memoria |
|---------|----------------|-------------|----------------|---------------|----------|---------|
| `agente_react_01.py` | ✅ | ❌ | ❌ | ❌ | Consola | ❌ |
| `agente_react_02.py` | ✅ | ✅ | ❌ | ❌ | Consola | ❌ |
| `agente_react_03.py` | ✅ | ✅ | ✅ | ❌ | Consola | ❌ |
| `agente_react_04.py` | ✅ | ✅ | ✅ | ✅ | Consola | ❌ |
| `agente_react_05_CLI.py` | ✅ | ✅ | ✅ | ✅ | Consola Interactiva | ❌ |
| `agente_react_06_streamlit.py` | ✅ | ✅ | ✅ | ✅ | Web (Streamlit) | ❌ |
| `agente_react_07_memory.py` | ✅ | ✅ | ✅ | ✅ | Web (Streamlit) | ✅ (Funcional) |

---

## Evolución de Características

### Parsing de Inputs
1. **Básico** (`agente_react_01.py`): String directo
2. **Tuplas** (`agente_react_02.py`): `ast.literal_eval()` para múltiples parámetros
3. **Diferenciado** (`agente_react_03.py`+): Parsing específico según tipo de tool
4. **Robusto** (`agente_react_04.py`+): Try-except para manejo de errores

### Interfaz de Usuario
1. **Script único** (`agente_react_01.py` - `agente_react_04.py`): Ejecución una vez
2. **Consola interactiva** (`agente_react_05_CLI.py`): Loop con `input()`
3. **Web UI** (`agente_react_06_streamlit.py` - `agente_react_07_memory.py`): Streamlit

### Capacidades del Agente
1. **Básico**: Solo operaciones sobre texto
2. **Matemáticas**: Operaciones numéricas simples y complejas
3. **Búsqueda web**: Acceso a información actualizada
4. **Memoria** (implementado): Contexto conversacional funcional en `agente_react_07_memory.py`

---

## Recomendaciones de Uso

- **Para aprender:** Comenzar con `agente_react_01.py` y seguir el orden de evolución
- **Para desarrollo:** Usar `agente_react_05_CLI.py` para pruebas rápidas en consola
- **Para producción/demo:** Usar `agente_react_07_memory.py` (versión completa con memoria conversacional)
- **Para pruebas rápidas:** Usar `agente_react_06_streamlit.py` (sin memoria, más ligero)

---

## Notas Técnicas

- Todos los archivos usan el mismo modelo: `gpt-4o-mini`
- Todos incluyen `AgentCallbackHandler` para depuración
- El parsing diferenciado es necesario porque LangChain pasa los inputs como strings que requieren procesamiento según el tipo de tool
- Tavily requiere API key configurada en variables de entorno
- Streamlit requiere instalación: `pip install streamlit`
- **Documentación de herramientas:** Todas las herramientas incluyen documentación estructurada con Description, Input, Output y Example
- **Idioma:** La mayoría de los archivos han sido traducidos al español (inputs, mensajes e interfaces)

---

## Dependencias Comunes

- `langchain`
- `langchain-openai`
- `langchain-community` (para Tavily)
- `python-dotenv`
- `streamlit` (solo para agente_react_06_streamlit.py y agente_react_07_memory.py)

## Archivos Adicionales

### `mis_tools.py`
**Objetivo:** Centralizar las herramientas del agente para reutilización.

**Contenido:**
- `get_text_length`: Calcula la longitud de un texto
- `multiplica2`: Multiplica dos números
- `math_operation`: Evalúa expresiones matemáticas
- `web_search_tool`: Herramienta de búsqueda web con Tavily
- `find_tool_by_name`: Función helper para buscar herramientas por nombre

**Uso:** Importado por `agente_react_07_memory.py` para mantener el código modular y organizado.

### `callbacks.py`
**Objetivo:** Proporcionar callbacks personalizados para depuración del agente.

**Contenido:**
- `AgentCallbackHandler`: Clase que imprime prompts y respuestas del LLM para depuración

**Uso:** Utilizado en todos los scripts del agente para monitorear la comunicación con el modelo.

