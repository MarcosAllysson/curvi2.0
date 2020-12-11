from typing import Any, Text, Dict, List, Union, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# importação validação form para validar slots
from rasa_sdk.forms import FormValidationAction

# para requisições a api
import requests

# expressão regular para validar nome -> Regular Expression
import re

# para lidar com data
from datetime import date


# DOUGLAS API
def generate_pdf(name, age, address, city, state, cellphone, email, linkedln_link, area, area_level, goal, scholarity, 
                courseName, courseSchool, courseEndYear, courses, companyName, companyOccupation, companyDescription, 
                companyStartEnd, feedback, grade):
    request_url = "https://curvi-api.herokuapp.com/api/user"

    info = {
        "name": name,
        "age": age,
        "address": address, 
        "city": city,
        "state": state,
        "cellphone": cellphone,
        "email": email,
        "linkedln_link": linkedln_link,
        "area": area,
        "area_level": area_level,
        "goal": goal,
        "scholarity": scholarity,
        "courseName": courseName, 
        "courseSchool": courseSchool,
        "courseEndYear": courseEndYear,
        "courses": courses,
        "companyName": companyName,
        "companyOccupation": companyOccupation,
        "companyDescription": companyDescription,
        "companyStartEnd": companyStartEnd,
        "feedback": feedback,
        "grade": grade
    }

    try:
        # make the API call
        response = requests.post(
            request_url, data=info
        )
        response.raise_for_status()
        

    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    print(response.json())
    return response
    print(response.status_code)



# DADOS BASICOS FORM VERIFICAÇÃO 2.0
class ValidateDadosBasicosForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_dados_basicos_form"

    def validate_nome(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do nome e primeiro nome """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
            nome_completo = value.split()
            primeiro_nome = nome_completo[0]

            return {"nome": value.capitalize(), "primeiroNome": primeiro_nome.capitalize()}
        else: 
            dispatcher.utter_message("Desculpa, não entendi.")
            return {"nome": None}

    def validate_idade(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do idade """

        # conter apenas números
        if value.isdigit() and int(value) > 0 and int(value) < 100:
            return {"idade": value}
        else: 
            dispatcher.utter_message("Apenas número...")
            return {"idade": None}

    def validate_telefone(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validação do telefone """

        # verificando se é número e se contém 11 dígitos númericos
        if value.isdigit() and len(value) == 11:
            return {"telefone": value}
        else:
            dispatcher.utter_message("Não entendi. Insira apenas o DDD seguido do número.")
            return {"telefone": None}


    def validate_cep(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando CEP """

        # substituir ponto, e traço respectivamente
        cep = value.replace('.', '')
        new_cep = cep.replace('-', '')

        # TESTE AVULSO
        # if len(new_cep) == 8:
        #     return {"endereco": "Paranoá", "cidade": "Brasília", "estado": "DF", "cep": value}
        # else:
        #     dispatcher.utter_message("CEP deve conter 8 dígitos.")
        #     return {"cep": None}



        #CONECTANDO API, EXTRAINDO ENDEREÇO...
        # verificar se o valor contém 8 dígitos
        if len(new_cep) == 8:
            # conectando na API passando o CEP
            address = requests.get("https://viacep.com.br/ws/" + new_cep + "/json/").json()

            # se for inválido, printar mensagem de erro pedindo CEP novamente
            if address == {'erro': True}:
                dispatcher.utter_message("CEP inválido, vamos de novo.")
                return {"cep": None}

            # se for válido, printa endereço
            else:
                # pegar valor do endereco
                endereco = tracker.get_slot("endereco")

                # endereço recebe o valor vindo da chamada da API
                endereco = address['logradouro']
                bairro = address['bairro']
                localidade = address['localidade']
                uf = address['uf']
                
                # printando mensagem após endereço encontrado
                dispatcher.utter_message("Vi que seu endereço é: {}, {}, {} - {} \n".format(endereco, bairro, localidade, uf))
                
                # retornando slots com valores preenchidos
                return {"endereco": endereco, "cidade": localidade, "estado": uf, "cep": cep}
        
        # printar erro se não tiver 8 dígitos
        else:
            dispatcher.utter_message("CEP inválido, vamos de novo.")
            return {"cep": None}


    def validate_email(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando email com RE """

        if re.findall(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", value):
        # if value != '':
            return {"email": value.lower()}
        else:
            dispatcher.utter_message("Email inválido...")
            return {"email": None}






# LINKEDLN FORM
class ValidateLinkedlnForm(FormValidationAction):
    """ Início do formulário """
    def name(self) -> Text:
        """ Nome do formulário """
        return "validate_linkedln_form"

    def validate_linkedln_link(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando linkedln_link """

        # usar RE pra validar URL
        # if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
        if value != '':
            return {"linkedln_link": value.lower()}
        else: 
            # dispatcher.utter_message("Vamos de novo! ")
            return {"linkedln_link": None}


# FORMACAO FORM
class ValidateFormacaoForm(FormValidationAction):
    def name(self) -> Text:
        """ Validando formação form """
        return "validate_formacao_form"

    def validate_area(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando area """

        """1 Vendas 
           2 Marketing 
           3 Tecnologia
           4 Direito 
           5 Saúde
           6 RH 
           7 Administração
           8 Contabilidade
           9 Projetos 
           10 Engenharia 
           11 Outros"""

        if value.isdigit():
            if int(value) == 1:
                return {"area": "Vendas"}
            elif int(value) == 2:
                return {"area": "Marketing"}
            elif int(value) == 3:
                return {"area": "Tecnologia"}
            elif int(value) == 4:
                return {"area": "Direito"}
            elif int(value) == 5:
                return {"area": "Saúde"}
            elif int(value) == 6:
                return {"area": "RH"}
            elif int(value) == 7:
                return {"area": "Administração"}
            elif int(value) == 8:
                return {"area": "Contabilidade"}
            elif int(value) == 9:
                return {"area": "Projetos"}
            elif int(value) == 10:
                return {"area": "Engenharia"}
            elif int(value) == 11:
                return {"area": "Outros"}
            else:
                dispatcher.utter_message("Só entre 1 e 11")
                return {"area": None}
        else: 
            dispatcher.utter_message("Vamos de novo! Só número. ")
            return {"area": None}


    def validate_area_nivel(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando area_nivel """

        """ 1 Estagiário(a)
                  2 Jovem aprendiz
                  3 Júnior
                  4 Sênior
                  5 Pleno"""

        if value.isdigit():
            if int(value) == 1:
                return {"area_nivel": "Estagiário(a)"}
            elif int(value) == 2:
                return {"area_nivel": "Jovem aprendiz"}
            elif int(value) == 3:
                return {"area_nivel": "Júnior"}
            elif int(value) == 4:
                return {"area_nivel": "Sênior"}
            elif int(value) == 5:
                return {"area_nivel": "Pleno"}
            else:
                dispatcher.utter_message("Só entre 1 e 5")
                return {"area_nivel": None}
        else: 
            dispatcher.utter_message("Vamos de novo! Só número. ")
            return {"area_nivel": None}


    def validate_objetivo(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando objetivo """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        # if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
        if value != '':
            # slot recebe valor inserido devidamente aprovado pelo regular expressions
            return {"objetivo": value.capitalize()}
        else: 
            dispatcher.utter_message("Vamos de novo! ")
            return {"objetivo": None}


    def validate_escolaridade(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando escolaridade """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        # if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
        if value != '':
            # slot recebe valor inserido devidamente aprovado pelo regular expressions
            return {"escolaridade": value.capitalize()}
        else: 
            dispatcher.utter_message("Vamos de novo! ")
            return {"escolaridade": None}

    
    def validate_cursoNome(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando curso """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        # if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
        if value != '':
            # slot recebe valor inserido devidamente aprovado pelo regular expressions
            return {"cursoNome": value}
        else: 
            dispatcher.utter_message("Vamos de novo! ")
            return {"cursoNome": None}


    def validate_institutoNome(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando instituição """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        # if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
        if value != '':
            # slot recebe valor inserido devidamente aprovado pelo regular expressions
            return {"institutoNome": value}
        else: 
            dispatcher.utter_message("Vamos de novo! ")
            return {"institutoNome": None}


    def validate_previsaoTermino(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando previsão de término """

        # ano_imput = value
        ano_atual = date.today().year

        # verificação se contém 4 dígitos, é número e maior ou igual ao ano atual
        if value.isdigit():
            if len(value) == 4 and int(value) >= int(ano_atual):
                return {"previsaoTermino": value}
            else:
                dispatcher.utter_message("Somente o ano! Lembre-se que você só pode terminar o curso esse ano, {}, em diante...".format(ano_atual))
                return {"previsaoTermino": None}
        else:
            dispatcher.utter_message("Não entendi...")
            return {"previsaoTermino": None}



# CURSO FORM
class ValidateCursoForm(FormValidationAction):
    def name(self) -> Text:
        """ Validando formação form """
        return "validate_cursos_form"

    
    def validate_habilidade(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando cursos """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        # if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
        if value != '':
            # slot recebe valor inserido devidamente aprovado pelo regular expressions
            return {"habilidade": value.capitalize()}
        else: 
            dispatcher.utter_message("Me fala de novo quais cursos você possui, não entendi... ")
            return {"habilidade": None}



# EXPERIENCIA FORM
class ValidateExperienciaForm(FormValidationAction):
    def name(self) -> Text:
        """ Validando formação form """
        return "validate_experiencia_form"

    def validate_cargo(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando cargo """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        # if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
        if value != '':
            # slot recebe valor inserido devidamente aprovado pelo regular expressions
            return {"cargo": value.capitalize()}
        else: 
            dispatcher.utter_message("Não entendi seu cargo. Vamos de novo! ")
            return {"cargo": None}


    def validate_nomeEmpresa(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando nome da empresa """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        # if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
        if value != '':
            return {"nomeEmpresa": value.capitalize()}
        else: 
            dispatcher.utter_message("Não entendi o nome da empresa. Me fala de novo... ")
            return {"nomeEmpresa": None}

    
    def validate_cargo_data_entrada_saida(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando saída do emprego """

        # ano_imput = value
        # ano_atual = date.today().year

        # verificação se contém 4 dígitos, é número e maior ou igual ao ano atual
        if value != '':
            return {"cargo_data_entrada_saida": value}
        else:
            dispatcher.utter_message("Não entendi...")
            return {"cargo_data_entrada_saida": None}


    def validate_cargo_descricao(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando descrição do cargo """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        # if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
        if value != '':
            return {"cargo_descricao": value.capitalize()}
        else: 
            dispatcher.utter_message("Me fala de novo, não entendi... ")
            return {"cargo_descricao": None}


# FEEDBACK FORM
class ValidateFeedbackForm(FormValidationAction):
    def name(self) -> Text:
        """ Validando formação form """
        return "validate_feedback_form"

    
    def validate_feedback(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando feedback """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        # if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
        if value != '':
            return {"feedback": value}
        else: 
            dispatcher.utter_message("Vamos de novo... ")
            return {"feedback": None}


    def validate_nota(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando nota """

        # aceitar apenas número entre 1 e 10
        if value.isdigit() and int(value) > 0 and int(value) < 11:
            return {"nota": value}
        else: 
            dispatcher.utter_message("Vamos de novo... ")
            return {"nota": None}




# FUNCTION THAT REPLACED SUBMIT() IN THE FORMS
class ActionSubmitResume(Action):
    def name(self) -> Text:
        return "action_submit_resume"

    def run (self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any], 
    ) -> List[Dict]:

        # send info to API on heroku
        name = tracker.get_slot("nome")
        age = tracker.get_slot("idade")
        address = tracker.get_slot("endereco")
        city = tracker.get_slot("cidade")
        state = tracker.get_slot("estado")
        cellphone = tracker.get_slot("telefone")
        email = tracker.get_slot("email")

        linkedln_link = tracker.get_slot("linkedln_link")
        if linkedln_link == None:
            linkedln_link = "NOT_PRINT"

        area = tracker.get_slot("area")
        area_level = tracker.get_slot("area_nivel")
        goal = tracker.get_slot("objetivo")
        scholarity = tracker.get_slot("escolaridade")
        courseName = tracker.get_slot("cursoNome")
        courseSchool = tracker.get_slot("institutoNome")
        courseEndYear = tracker.get_slot("previsaoTermino")

        courses = tracker.get_slot("habilidade")
        if courses == None:
            courses = "NOT_PRINT"

        companyName = tracker.get_slot("nomeEmpresa")
        if companyName == None:
            companyName = "Primeiro emprego objetivando adquirir conhecimento e experiência necessária junto à empresa."

        companyOccupation = tracker.get_slot("cargo")
        if companyOccupation == None:
            companyOccupation = "NOT_PRINT"

        companyDescription = tracker.get_slot("cargo_descricao")
        if companyDescription == None:
            companyDescription = "NOT_PRINT"

        companyStartEnd = tracker.get_slot("cargo_data_entrada_saida")
        if companyStartEnd == None:
            companyStartEnd = "NOT_PRINT"

        feedback = tracker.get_slot("feedback")
        grade = tracker.get_slot("nota")
        

        # CHAMADA DA FUNÇÃO PASSANDO OS DADOS PRA FAZER POST REQUEST
        # generate_pdf(name, age, address, city, state, cellphone, email, linkedln_link, area, area_level, goal, scholarity, 
        #         courseName, courseSchool, courseEndYear, courses, companyName, companyOccupation, companyDescription, 
        #         companyStartEnd, feedback, grade)


        # return []


        # após post request, zerando todos os slots para None
        return [
            SlotSet("nome", None),
            SlotSet("idade", None),
            SlotSet("endereco", None),
            SlotSet("cidade", None),
            SlotSet("estado", None),
            SlotSet("telefone", None),
            SlotSet("email", None),
            SlotSet("linkedln_link", None),
            SlotSet("area", None),
            SlotSet("area_nivel", None),
            SlotSet("objetivo", None),
            SlotSet("escolaridade", None),
            SlotSet("cursoNome", None),
            SlotSet("institutoNome", None),
            SlotSet("previsaoTermino", None),
            SlotSet("habilidade", None),
            SlotSet("nomeEmpresa", None),
            SlotSet("cargo", None),
            SlotSet("cargo_descricao", None),
            SlotSet("cargo_data_entrada_saida", None),
            SlotSet("feedback", None),
            SlotSet("nota", None)
        ]