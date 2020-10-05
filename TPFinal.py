import spacy
import es_core_news_md
import os
from spacy.matcher import Matcher
from collections import Counter


# Anotations: https://spacy.io/api/annotation

os.system('clear') 


valor_leer = input("Caso de estudio completo S/N?")

contenido = ""

if valor_leer == "S":
    f = open("casoestudio.txt", "r")
    contenido = f.read()

if valor_leer == "N":
    f = open("casoestudiocorto.txt", "r")
    contenido = f.read()


#------------------------------------------------------------------------------------------------------------------------------------
# Modulo Identificación de simbolos más usados: Tokenizo el documento, eliminación de ruido, armado de listas de palabras más usadas
#------------------------------------------------------------------------------------------------------------------------------------

print("Inicializando modelo en Español\r\n")

nlp = es_core_news_md.load()

contenido_sin_espacios = contenido.replace("\n", " ")
doc = nlp(contenido_sin_espacios)


contenido = [(token.text,token.pos_,token.lemma_,token.dep_) for token in doc if token.is_stop != True and token.is_punct != True ]

#print(contenido)
#input("Presione una tecla")

sujetos_documento = [(token.lemma_,token.dep_) for token in doc if token.is_stop != True and token.is_punct != True and token.dep_ == "nsubj" ]

frecuencia_sujetos = Counter(sujetos_documento)
sujetos_mas_usados = frecuencia_sujetos.most_common(30)

print("Los 30 sujetos (lematizados) mas usados en el doc: ")
print(sujetos_mas_usados)
print("\r\n")

sustantivos_documento = [(token.lemma_,token.dep_) for token in doc if token.is_stop != True and token.is_punct != True and token.pos_ == "NOUN" ]

frecuencia_sustantivos = Counter(sustantivos_documento)
sustantivos_mas_usados = frecuencia_sustantivos.most_common(20)

print("Los 20 sustantivos (lematizados) mas usados en el doc: ")
print(sustantivos_mas_usados)
print("\r\n")

verbos_documento = [token.lemma_ for token in doc if token.is_stop != True and token.is_punct != True and token.pos_ == "VERB" ]

frecuencia_verbos = Counter(verbos_documento)
verbos_mas_usados = frecuencia_verbos.most_common(15)

print("Los 15 verbos (lematizados) mas usados en el doc: ")
print(verbos_mas_usados)
print("\r\n")

adjetivos_doc = [token.lemma_ for token in doc if token.is_stop != True and token.is_punct != True and token.pos_ == "ADJ" ]

frecuencia_adjetivos = Counter(adjetivos_doc)
adjetivos_mas_usados = frecuencia_adjetivos.most_common(10)

print("Los 10 adjetivos (lematizados) mas usados en el doc: ")
print(adjetivos_mas_usados)
print("\r\n")

print("Listas de control generadas. Presione una ENTER para continuar")
input()

#------------------------------------------------------------------------------------------------------------------------------------
# Modulo de Identificación de frases: patrones para reconocimiento de frases y armado de listas
#------------------------------------------------------------------------------------------------------------------------------------

# Inicializa el matcher con el vocabulario compartido
matcher = Matcher(nlp.vocab)

# Añade el patrón al matcher
pattern_verb1 = [{"POS": "VERB"}, {"POS": "NOUN"}]
pattern_verb2 = [{"POS": "VERB"}, {"POS": "DET"} ,{"POS": "NOUN"}]
pattern_verb3 = [{"POS": "VERB"}, {"POS": "ADP"} ,{"POS": "VERB"}]
pattern_verb4 = [{"POS": "VERB"}, {"POS": "VERB"}]

matcher.add("VERB_PHRASE_PATTERN", None, pattern_verb1)
matcher.add("VERB_PHRASE_PATTERN", None, pattern_verb2)
matcher.add("VERB_PHRASE_PATTERN", None, pattern_verb3)
matcher.add("VERB_PHRASE_PATTERN", None, pattern_verb4)

# Añadir los patrones para los objetos
pattern_obj1 = [{"POS": "NOUN"}, {"POS": "ADP"} ,{"POS": "NOUN"}]
pattern_obj2 = [{"POS": "NOUN"}, {"POS": "ADP"} ,{"POS": "DET"} ,{"POS": "NOUN"}] 
pattern_obj3 = [{"POS": "NOUN"}, {"POS": "ADJ"}]

matcher.add("OBJ_PHRASE_PATTERN", None, pattern_obj1)
matcher.add("OBJ_PHRASE_PATTERN", None, pattern_obj2)
matcher.add("OBJ_PHRASE_PATTERN", None, pattern_obj3)

pattern_subj1 = [{"POS": "NOUN"}, {"POS": "ADP"} ,{"POS": "NOUN"}]

matcher.add("SUBJ_PHRASE_PATTERN_1", None, pattern_subj1)

# Añadir los patrones para los estados
pattern_state = [{"POS": "NOUN"}, {"POS": "ADP"} ,{"POS": "NOUN"}, {"POS": "ADJ"}]

matcher.add("STATE_PHRASE_STATE", None, pattern_state)

#realizar el match de los patrones y almacenarlo en una lista
matches = matcher(doc)

sujeto_candidatos= set([])
objetos_candidatos = set([])
verbos_candidatos = set([])
estados_candidatos = set([])

# Itera sobre los resultados
for match_id, start, end in matches:
    # Obtén el span resultante
    string_id = nlp.vocab.strings[match_id]  # Get string representation
    
    if string_id=="OBJ_PHRASE_PATTERN":
        matched_span = doc[start:end]

        objetos_candidatos.add(matched_span)

    if string_id=="SUBJ_PHRASE_PATTERN_1":
        matched_span = doc[start:end]
   
        if matched_span[0].dep_ == "obj" and matched_span[1].dep_ == "case" and matched_span[2].dep_ == "nmod":
            sujeto_candidatos.add(matched_span)

        if matched_span[0].dep_ == "obl" and matched_span[1].dep_ == "case" and matched_span[2].dep_ == "nmod":
            sujeto_candidatos.add(matched_span)

        if matched_span[0].dep_ == "nmod" and matched_span[1].dep_ == "case" and matched_span[2].dep_ == "nmod":
            sujeto_candidatos.add(matched_span)

        if matched_span[0].dep_ == "appos" and matched_span[1].dep_ == "case" and matched_span[2].dep_ == "nmod":
            sujeto_candidatos.add(matched_span) 

        if matched_span[0].dep_ == "nsubj" and matched_span[1].dep_ == "case" and matched_span[2].dep_ == "nmod":
            sujeto_candidatos.add(matched_span)

    if string_id=="VERB_PHRASE_PATTERN":
        matched_span = doc[start:end]
        verbos_candidatos.add(matched_span)

    if string_id=="STATE_PHRASE_STATE":
        matched_span = doc[start:end]
        estados_candidatos.add(matched_span)


print("Los Objetos candidatos matcheados con los patrones son:")
print(objetos_candidatos)
print("\r\n")

print("Los Sujetos candidatos matcheados con los patrones son:")
print(sujeto_candidatos)
print("\r\n")

print("Los Verbos candidatos matcheados con los patrones son:")
print(verbos_candidatos)
print("\r\n")


print("Los Estados candidatos matcheados con los patrones son:")
print(estados_candidatos)
print("\r\n")

print("Listas de simbolos del LEL candidatos generadas. Presione una ENTER para continuar")
input()

#------------------------------------------------------------------------------------------------------------------------------------
# Modulo de Filtrado de listado de frases: verifico existencia de las frases candidatas en listado de palabras más usadas
#------------------------------------------------------------------------------------------------------------------------------------


verbos_finales_repetidos = []
#verifico que la frase verbal este dentro de los verbos mas usados
for frase_verbal in verbos_candidatos:
    #print("Analizo frase: " + frase_verbal.text)
    for verbo_usado in verbos_mas_usados:
        primer_palabra_verbo = frase_verbal[0].lemma_
        if verbo_usado[0] == primer_palabra_verbo:
            #print("Incluyo la frase verbal")
            #print(primer_palabra_verbo)
            #print(verbo_usado[0])
            verbos_finales_repetidos.append(frase_verbal)
            continue

verbos_finales_limpios = set([])
for estado_ in verbos_finales_repetidos:
    verbos_finales_limpios.add(estado_.text)


estados_finales_repetidos = []
#verifico que los estados este dentro de los verbos mas usados
for frase_estado in estados_candidatos:
    #print("Analizo frase: " + frase_estado.text)
    for adjetivo_usado in adjetivos_mas_usados:
        ultima_palabra_frase_estado = frase_estado[3].lemma_
        if adjetivo_usado[0] == ultima_palabra_frase_estado:
            #print("Incluyo la frase estado")
            #print(ultima_palabra_frase_estado)
            #print(adjetivo_usado[0])
            estados_finales_repetidos.append(frase_estado)
            continue

estados_finales_limpios = set([])
for estado_ in estados_finales_repetidos:
    estados_finales_limpios.add(estado_.text)



objetos_finales_con_repetidos = []
#verifico que los estados este dentro de los verbos mas usados
for frase_objeto in objetos_candidatos:
    #print("Analizo frase: " + frase_objeto.text)
    for sustantivo_usado in sustantivos_mas_usados:
        primer_palabra_sustantivo = frase_objeto[0].lemma_
        if sustantivo_usado[0][0] == primer_palabra_sustantivo:
            #print("Incluyo la frase objeto")
            #print(primer_palabra_sustantivo)
            #print(sustantivo_usado[0])
            #print(frase_objeto)

            objetos_finales_con_repetidos.append(frase_objeto)
            continue

objetos_finales_limpios = set([])
for objeto_ in objetos_finales_con_repetidos:
    objetos_finales_limpios.add(objeto_.text)


sujetos_finales_con_repetidos = []
#verifico que los estados este dentro de los verbos mas usados
for frase_sujeto in sujeto_candidatos:
    #print("Analizo frase: " + frase_sujeto.text)
    for sustantivo_usado in sujetos_mas_usados:
        primer_palabra_sustantivo = frase_sujeto[0].lemma_
        if sustantivo_usado[0][0] == primer_palabra_sustantivo:
            #print("Incluyo la frase sujeto")
            #print(primer_palabra_sustantivo)
            #print(sustantivo_usado[0])
            #print(frase_sujeto)

            sujetos_finales_con_repetidos.append(frase_sujeto)            
            continue

sujetos_finales_limpios = set([])
for sujeto_ in sujetos_finales_con_repetidos:
    sujetos_finales_limpios.add(sujeto_.text)


print("Listas finales de SUJETOS, OBJETOS, VERBOS y ESTADOS:")

print("VERBOS obtenidos:")
print(verbos_finales_limpios)
print("Cant. VERBOS")
print(len(verbos_finales_limpios))
print("\r\n")

print("ESTADOS obtenidos:")
print(estados_finales_limpios)
print("Cant. ESTADOS")
print(len(estados_finales_limpios))
print("\r\n")

print("SUJETOS obtenidos:")
print(sujetos_finales_limpios)
print("Cant. SUJETOS")
print(len(sujetos_finales_limpios))
print("\r\n")

print("OBJETOS obtenidos:")
print(objetos_finales_limpios)
print("Cant. OBJETOS")
print(len(objetos_finales_limpios))

input("Para ver los resultados de control presione ENTER")

#------------------------------------------
# Mecanismo de control 
#------------------------------------------

#Proceso de control sujetos
sujetos_de_control = ["Distribuidora",
"Cliente",
"Oficina comercial",
"Oficina de administración",
"Oficina de planificación",
"Jefe de producción",
"Jefe comercial",
"Oficial planificador",
"Encargado de planta",
"Encargado del turno",
"Encargado de depósito",
"Papelera Sudeste"]

sujeto_count = 0
for sujeto_ in sujetos_finales_limpios:
    for sujeto_control_ in sujetos_de_control:
        if (sujeto_.lower() == sujeto_control_.lower()):
            sujeto_count = sujeto_count + 1
            print(sujeto_)

print("Cantidad de sujetos de control: " + str(len(sujetos_de_control)))
print("Cantidad de sujetos encontrados: " + str(sujeto_count))


#Proceso de control sujetos
objetos_de_control = ["Orden de compra",
"Materia prima",
"Caja de cartón",
"Cajas de solapa",
"Cajas de cartón de tapa y fondo",
"Accesorios de cartón",
"Máquina de fabricación",
"Máquina de corte",
"Máquina de impresión",
"Máquina que cuenta y empaqueta",
"Orden de producción",
"Programa de producción",
"Informe de retraso",
"Formulario de informe de dificultades de fabricación",
"Programa de fabricación extraordinario",
"Turno de fabrica",
"Política comercial",
"Fecha de entrega"]

objeto_count = 0
for objeto_ in objetos_finales_limpios:
    for objeto_control_ in objetos_de_control:
        if (objeto_.lower() == objeto_control_.lower()):
            objeto_count = objeto_count + 1
            print(objeto_)

print("Cantidad de objetos de control: " + str(len(objetos_de_control)))
print("Cantidad de objetos encontrados: " + str(objeto_count))


#Proceso de control sujetos
verbos_de_control = ["Planificar la producción",
"Elaborar la orden de producción",
"Revisar los programas de fabricación",
"Informar dificultad de fabricación",
"Comunicación con Papelera Sudeste",
"Ordenar cajas",
"Pedido de cajas"
"Fabricación de cajas",
"Entregar cajas",
"Estudiar fallas de fabricación"]

verbos_count = 0
for verbo_ in verbos_finales_limpios:
    for verbo_control_ in verbos_de_control:
        if (verbo_.lower() == verbo_control_.lower()):
            verbos_count = verbos_count + 1
            print(verbo_)

print("Cantidad de verbos de control: " + str(len(verbos_de_control)))
print("Cantidad de verbos encontrados: " + str(verbos_count))


#Proceso de control sujetos
estados_de_control = ["Cajas a medida",
"Cajas de tamaño fijo",
"Orden de compra anticipada",
"Orden de compra común",
"Orden de compra urgente",
"Orden de producción terminada",
"Orden de producción incompleta",
"Orden de producción pendiente",
"Orden de producción urgente"
]

estados_count = 0
for estado_ in estados_finales_limpios:
    for estado_control_ in estados_de_control:
        if (estado_.lower() == estado_control_.lower()):
            estados_count = estados_count + 1
            print(estado_)

print("Cantidad de estados de control: " + str(len(estados_de_control)))
print("Cantidad de estados encontrados: " + str(estados_count))