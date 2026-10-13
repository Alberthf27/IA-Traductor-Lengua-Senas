import re

class MorphosyntacticSentenceAssembler:
    """
    Ensamblador Morfosintáctico Frugal (Reglas Lingüísticas en Tiempo Real).
    Transforma listas de señas aisladas en lenguaje natural coherente en español,
    aplicando concordancia, modismos corteses y signos de entonación.
    """
    PHRASE_PATTERNS = [
        # Saludos y cortesía
        (["Hola", "Amigo"], "¡Hola, amigo!"),
        (["Buenos días", "Profesor"], "¡Buenos días, profesor!"),
        (["Buenos días", "Amigo"], "¡Buenos días, amigo!"),
        (["Por favor", "Agua"], "Por favor, ¿me das un vaso de agua?"),
        (["Agua", "Por favor"], "Un vaso de agua, por favor."),
        (["Por favor", "Ayuda"], "¡Por favor, necesito ayuda!"),
        (["Ayuda", "Por favor"], "¡Necesito ayuda, por favor!"),
        (["Sí", "Gracias"], "Sí, muchas gracias."),
        (["No", "Gracias"], "No, muchas gracias."),
        (["Comer", "Por favor"], "Tengo hambre, por favor."),
        (["Beber", "Por favor"], "Tengo sed, por favor."),
        (["Ir", "Casa"], "Quiero ir a casa."),
        (["Ir", "Escuela"], "Voy a la escuela."),
    ]

    SINGLE_WORD_ENHANCEMENT = {
        "Hola": "¡Hola!",
        "Adiós": "¡Hasta luego!",
        "Gracias": "¡Muchas gracias!",
        "Por favor": "Por favor.",
        "Ayuda": "¡Necesito ayuda!",
        "Disculpa": "Disculpa la molestia.",
        "Buenos días": "¡Buenos días!",
        "Buenas noches": "¡Buenas noches!",
        "Tarde": "¡Buenas tardes!",
        "Amor": "Te quiero mucho.",
        "Feliz": "Estoy muy feliz.",
        "Triste": "Me siento triste.",
        "Cansado": "Estoy cansado.",
        "Agua": "Agua.",
        "Comida": "Comida.",
    }

    def assemble(self, tokens):
        """
        tokens: lista de palabras en español predichas por el reconocedor.
        Retorna la oración ensamblada de forma natural.
        """
        if not tokens:
            return ""

        # 1. Agrupar dactilología consecutiva (letras sueltas como 'H', 'O', 'L', 'A') en palabras
        merged_tokens = []
        letter_buffer = []

        for t in tokens:
            clean_t = t.strip()
            if len(clean_t) == 1 and clean_t.isalpha():
                letter_buffer.append(clean_t)
            else:
                if letter_buffer:
                    merged_tokens.append("".join(letter_buffer).capitalize())
                    letter_buffer = []
                merged_tokens.append(clean_t)

        if letter_buffer:
            merged_tokens.append("".join(letter_buffer).capitalize())

        if not merged_tokens:
            return ""

        # 2. Si es una sola palabra clave, aplicar enriquecimiento expresivo
        if len(merged_tokens) == 1:
            return self.SINGLE_WORD_ENHANCEMENT.get(merged_tokens[0], merged_tokens[0])

        # 3. Búsqueda de patrones fraseológicos
        text_joined = " ".join(merged_tokens)
        for pattern_list, enhanced_phrase in self.PHRASE_PATTERNS:
            pattern_str = " ".join(pattern_list)
            if pattern_str.lower() in text_joined.lower():
                text_joined = re.sub(re.escape(pattern_str), enhanced_phrase, text_joined, flags=re.IGNORECASE)
                return text_joined

        # 4. Fallback sintáctico: Primera mayúscula y punto final
        sentence = " ".join(merged_tokens).strip()
        sentence = sentence[0].upper() + sentence[1:]
        if not sentence.endswith((".", "!", "?")):
            sentence += "."

        return sentence
