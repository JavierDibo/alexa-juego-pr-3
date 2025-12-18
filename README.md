1. # **Introducción**

El objetivo de esta práctica es desarrollar y poner en marcha un modelo de diálogo para Alexa, utilizando Amazon Developers.

Esta práctica se enmarca dentro de la asignatura *Interfaces de Usuario Multimodales* del Máster en Ingeniería Informática, y está orientada a introducir al estudiante en el desarrollo de interfaces conversacionales mediante asistentes virtuales.

El trabajo se organiza en varias fases que abarcan tanto la creación del skill en Amazon Developer, como la preparación del entorno de desarrollo en Python y la implementación del código que gestionará las peticiones de los usuarios. Todo ello permite familiarizarse con tecnologías ampliamente utilizadas en la creación de asistentes de voz comerciales, así como comprender los modelos de interacción basados en lenguaje natural.

2. # **Arquitectura**

Para desarrollar el modelo de lenguaje lo primero que se debe hacer es preparar la invocación de la skill. Tras esto pasamos a crear los intents necesarios para ir modelando dicha skill. Estos intents son:

1. ## **ChooseGameIntent**

Este intent se utiliza para permitir al usuario seleccionar un juego disponible dentro de la skill de Alexa. Valida si el juego solicitado es válido y lo inicia en caso afirmativo.

* Ejemplo de uso: "quiero jugar a {game}"

  2. ## **HowToPlayIntent**

Permite explicar las reglas del juego seleccionado por el usuario.

* Ejemplo de uso: "cómo se juega a {game}"

  3. ## **AnswerDigitsIntent**

Recibe la respuesta del usuario con la secuencia de números, comprueba si es correcta y se encarga de gestionar la lógica del juego (avanzar, repetir intento o finalizar).

* Ejemplo de uso: "es {digits}"

  4. ## **AMAZON.RepeatIntent**

Este intent de Amazon se utiliza para repetir una secuencia de números si el usuario lo solicita, aunque cuenta como fallo en el intento actual.

* Ejemplo de uso: "repite"

  5. ## **Slots**

En cuanto a los slots que se han definido para este modelo de diálogo, tenemos dos:

1. ## **{game}**

Es un slot personalizado que indica el juego que el usuario quiere jugar. En esta práctica, reconoce el juego "secuencia de números".

2. ## **{digits}**

De tipo AMAZON.searchQuery, recoge la secuencia de números dictada. Permite recibir entrada tanto en formato numérico como en palabras, que luego se procesa internamente.

3. # **Aspectos a destacar sobre el código**

La implementación del backend en Python se ha diseñado para ofrecer una experiencia robusta y flexible. Los puntos técnicos más relevantes son:

**Robustez en la captura de datos (parse\_digits):** Se ha implementado un sistema de normalización que permite al usuario dictar los números de forma natural. El código procesa tanto dígitos numéricos como palabras ("uno", "cero", etc.), eliminando signos de puntuación y espacios innecesarios para facilitar la comparación.  
**Lógica de Progresión y Reintentos:** El sistema gestiona automáticamente el avance entre niveles (de 3 a 9 dígitos). Cada nivel ofrece dos oportunidades con secuencias distintas; si se falla el segundo intento o se solicita repetir la secuencia (penalización), la partida finaliza.  
**Persistencia de Sesión:** Mediante el uso de session\_attributes, el backend mantiene el estado del juego (nivel actual, grupo e historial de puntuación) de forma persistente durante toda la interacción del usuario.  
**Gestión Dinámica de Respuestas:** El código centraliza la construcción de respuestas en funciones como prepare\_round y finish, asegurando una interacción coherente y personalizada según el desempeño del usuario.

4. # **Anexo**

Esta sección recoge los documentos relevantes al proyecto que no se pueden incluir directamente en la memoria.

## **4.1. Código fuente**

El código fuente se puede encontrar en el siguiente [repositorio de GitHub](https://github.com/JavierDibo/alexa-skill-en-lambda-aws).