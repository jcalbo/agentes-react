# Agentes LangChain REACT

Repositorio que implementa agentes REACT (Reasoning + Acting) utilizando LangChain, desde una implementación básica hasta versiones avanzadas con memoria e interfaz web.

## Descripción

Este repositorio contiene una serie de scripts sencillos que muestran cómo construir agentes de IA basados en Langchain utilizando el patrón REACT. 

Los agentes pueden:

- Realizar operaciones sobre texto
- Ejecutar cálculos matemáticos
- Buscar información en la web mediante Tavily
- Mantener contexto conversacional (versión avanzada)

## Inicio Rápido

### Requisitos Previos

- Python 3.10 o superior
- Credenciales en cualquier LLM que soporte Function Calling
- (Opcional) Cuenta de Tavily para búsqueda web

### Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd agentes_react
```

2. Crear y activar un entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

O si usas pipenv:
```bash
pipenv install
```

4. Configurar variables de entorno:
```bash
cp .evn_tavily .env
# Editar .env con tus API keys
```

Variables de entorno necesarias:
- `OPENAI_API_KEY`: Tu clave de API de OpenAI
- `TAVILY_API_KEY`: (Opcional) Tu clave de API de Tavily para búsqueda web

## 📁 Estructura del Proyecto

```
agentes_react/
├── agente_react_01.py          # Versión básica con una herramienta
├── agente_react_02.py          # Agrega herramientas con múltiples parámetros
├── agente_react_03.py          # Agrega evaluación de expresiones matemáticas
├── agente_react_04.py          # Integra búsqueda web con Tavily
├── agente_react_05_CLI.py      # Versión interactiva por consola
├── agente_react_06_streamlit.py # Interfaz web con Streamlit
├── agente_react_07_memory.py   # Versión completa con memoria conversacional
├── mis_tools.py                # Herramientas centralizadas
├── callbacks.py                # Callbacks para depuración
├── INDICE.md                   # Documentación detallada de cada versión
└── README.md                   # Este archivo
```

## Uso

### Versión Básica (Consola)

Ejecutar cualquiera de los scripts básicos:
```bash
python agente_react_01.py
python agente_react_02.py
python agente_react_03.py
python agente_react_04.py
```

### Versión Interactiva (CLI)

```bash
python agente_react_05_CLI.py
```

Escribe tus preguntas y presiona Enter. Escribe "END" para salir.

### Versión Web (Streamlit)

**Sin memoria:**
```bash
streamlit run agente_react_06_streamlit.py
```

**Con memoria:**
```bash
streamlit run agente_react_07_memory.py
```

La aplicación se abrirá en `http://localhost:8501`


## Características

### Herramientas Disponibles

- **`get_text_length`**: Calcula la longitud de un texto
- **`multiplica2`**: Multiplica dos números
- **`math_operation`**: Evalúa expresiones matemáticas complejas
- **`web_search_tool`**: Busca información en la web usando Tavily

### Características Avanzadas

- ✅ Parsing inteligente de inputs según el tipo de herramienta
- ✅ Manejo robusto de errores con try-except
- ✅ Búsqueda web como fallback automático
- ✅ Memoria conversacional (versión 07)
- ✅ Interfaz web moderna con Streamlit
- ✅ Callbacks para depuración y monitoreo

## Configuración

### Modelo LLM

En este caso, todos los scripts usan `gpt-4o-mini`, pero se puede cambiar a cualquier otr modelo editando la línea correspondiente en cada script:

```python
llm = ChatOpenAI(model="gpt-4o-mini", ...)
```

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con:

```env
OPENAI_API_KEY=tu_clave_openai
TAVILY_API_KEY=tu_clave_tavily
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=tu_clave_langchain  # Opcional, para LangSmith
```

## Documentación

- **[INDICE.md](INDICE.md)**: Documentación detallada de cada versión del agente, incluyendo objetivos, características y diferencias entre versiones.

## Contribuciones

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Documentación

- [LangChain](https://www.langchain.com/) por el framework
- [OpenAI](https://openai.com/) por los modelos de lenguaje
- [Tavily](https://tavily.com/) por la API de búsqueda web
- [Streamlit](https://streamlit.io/) por la plataforma de desarrollo web

## Contacto

Para preguntas o sugerencias, por favor abre un issue en el repositorio.

---

**Nota:** Este proyecto es personal y solo para aprender sobre agentes de IA y el patrón REACT. No está optimizado para producción.

