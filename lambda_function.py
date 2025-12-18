eximport re
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name

sb = SkillBuilder()

DIGITS_FORWARD = {
    3: {1: [5, 8, 2],                 2: [6, 9, 4]},
    4: {1: [6, 4, 3, 9],              2: [7, 2, 8, 6]},
    5: {1: [4, 2, 7, 3, 1],           2: [7, 5, 8, 3, 6]},
    6: {1: [6, 1, 9, 4, 7, 3],        2: [3, 9, 2, 4, 8, 7]},
    7: {1: [5, 9, 1, 7, 4, 2, 8],     2: [4, 1, 7, 9, 3, 8, 6]},
    8: {1: [5, 8, 1, 9, 2, 6, 4, 7],  2: [3, 8, 2, 9, 5, 1, 7, 4]},
    9: {1: [2, 7, 5, 8, 6, 2, 5, 8, 4], 2: [7, 1, 3, 9, 4, 2, 5, 6, 8]},
}

MENU_TEXT = (
    "Hola, vamos a jugar unos minutos. ¿A qué minijuego quieres jugar? "
    "Sólo puedes jugar al minijuego secuencia de números "
    "Si necesitas saber cómo se juega, ¡pregúntame!"
)

HOWTO_FORWARD = (
    "Voy a decir algunos números. Escuche con atención y cuando yo haya terminado, repítalos inmediatamente. "
    "¿Quieres jugar a secuencia de números?"
)

def say_sequence(seq):
    return " ".join(str(d) for d in seq)

def parse_digits(text):
    if not text:
        return []

    t = text.lower()

    # Normaliza separadores típicos
    t = t.replace("-", " ").replace(",", " ").replace(".", " ")

    word_map = {
        "cero": 0,
        "uno": 1, "un": 1,
        "dos": 2,
        "tres": 3,
        "cuatro": 4,
        "cinco": 5,
        "seis": 6,
        "siete": 7,
        "ocho": 8,
        "nueve": 9,
    }

    result = []

    for ch in t:
        if ch.isdigit():
            result.append(int(ch))

    if not result:
        # Tokeniza por espacios
        tokens = [tok.strip() for tok in t.split() if tok.strip()]
        for tok in tokens:
            tok = tok.strip("¡!¿?\"'():;")

            if tok in word_map:
                result.append(word_map[tok])

    return result

def start_game(attrs):
    attrs["state"] = "PLAYING"
    attrs["game"] = "DIGITS_FORWARD"
    attrs["series"] = 3
    attrs["group"] = 1
    attrs["best_score"] = 0
    attrs["repeat_penalty"] = False
    attrs["expected"] = DIGITS_FORWARD[3][1]

def prepare_round(attrs):
    series = attrs["series"]
    group = attrs["group"]
    seq = DIGITS_FORWARD[series][group]
    attrs["expected"] = seq
    attrs["repeat_penalty"] = False
    speak = f"Empezamos: {say_sequence(seq)}"
    reprompt = "Repítelos ahora, por favor."
    return speak, reprompt

def finish(attrs):
    score = attrs.get("best_score", 0)
    attrs["state"] = "END"
    return f"Hemos acabado. Tu puntuación de hoy: {score} puntos. ¡Enhorabuena!"

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak = "Hola. Vamos a jugar unos minutos. A que minijuego quieres jugar."

        return (
            handler_input.response_builder
            .speak(speak)
            .ask(speak)
            .response
        )

class ChooseGameIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ChooseGameIntent")(handler_input)

    def handle(self, handler_input):
        attrs = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        game_raw = slots.get("game").value if slots and slots.get("game") else ""
        game = (game_raw or "").strip().lower()

        if game != "secuencia de números":
            speak = (
                "Lo siento, no sé jugar a eso. "
                "Sólo puedes jugar al minijuego secuencia de números"
                "Si necesitas saber cómo se juega, ¡pregúntame!"
            )
            return (
                handler_input.response_builder
                .speak(speak)
                .ask("A que minijuego quieres jugar?")
                .response
            )

        start_game(attrs)
        speak, reprompt = prepare_round(attrs)
        return (
            handler_input.response_builder
            .speak(speak)
            .ask(reprompt)
            .response
        )

class HowToPlayIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("HowToPlayIntent")(handler_input)

    def handle(self, handler_input):
        return (
            handler_input.response_builder
            .speak(HOWTO_FORWARD)
            .ask("Dime: quiero jugar a secuencia de numeros.")
            .response
        )

class AnswerDigitsIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AnswerDigitsIntent")(handler_input)

    def handle(self, handler_input):
        attrs = handler_input.attributes_manager.session_attributes

        if attrs.get("state") != "PLAYING":
            return (
                handler_input.response_builder
                .speak("Primero elige un minijuego. " + MENU_TEXT)
                .ask("A que minijuego quieres jugar?")
                .response
            )

        slots = handler_input.request_envelope.request.intent.slots
        digits_raw = slots.get("digits").value if slots and slots.get("digits") else ""
        user_digits = parse_digits(digits_raw)

        expected = attrs.get("expected", [])
        series = attrs.get("series", 3)
        group = attrs.get("group", 1)

        if attrs.get("repeat_penalty"):
            correct = False
        else:
            correct = (user_digits == expected)

        if correct:
            attrs["best_score"] = max(attrs.get("best_score", 0), series)

            if series >= 9:
                return handler_input.response_builder.speak(finish(attrs)).set_should_end_session(True).response

            attrs["series"] = series + 1
            attrs["group"] = 1
            speak, reprompt = prepare_round(attrs)
            return (
                handler_input.response_builder
                .speak(speak)
                .ask(reprompt)
                .response
            )

        # incorrecto
        if group == 1:
            attrs["group"] = 2
            speak, reprompt = prepare_round(attrs)
            return (
                handler_input.response_builder
                .speak("No es correcto. Probamos otro intento. " + speak)
                .ask(reprompt)
                .response
            )

        return handler_input.response_builder.speak(finish(attrs)).set_should_end_session(True).response

class RepeatIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.RepeatIntent")(handler_input)

    def handle(self, handler_input):
        attrs = handler_input.attributes_manager.session_attributes
        if attrs.get("state") != "PLAYING":
            return (
                handler_input.response_builder
                .speak("No hay nada que repetir. " + MENU_TEXT)
                .ask("A que minijuego quieres jugar?")
                .response
            )

        attrs["repeat_penalty"] = True
        expected = attrs.get("expected", [])
        speak = f"De acuerdo, lo repito: {say_sequence(expected)}"
        return (
            handler_input.response_builder
            .speak(speak)
            .ask("Repitelos ahora, por favor.")
            .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        return (
            handler_input.response_builder
            .speak(MENU_TEXT)
            .ask("A que minijuego quieres jugar?")
            .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        return handler_input.response_builder.speak("¡Vale! Hasta luego.").set_should_end_session(True).response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        return (
            handler_input.response_builder
            .speak("Lo siento, ha ocurrido un error. Intentalo otra vez.")
            .ask("Puedes decir: quiero jugar a secuencia de numeros.")
            .response
        )

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ChooseGameIntentHandler())
sb.add_request_handler(HowToPlayIntentHandler())
sb.add_request_handler(AnswerDigitsIntentHandler())
sb.add_request_handler(RepeatIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()