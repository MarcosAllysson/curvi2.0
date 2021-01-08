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
                courseName, courseSchool, courseEndYear, courses, language, language_level, cientificResearch, companyName, 
                companyOccupation, companyDescription, companyStartEnd, companyNameVolunteer, companyOccupationVolunteer,
                companyDescriptionVolunteer, companyStartEndVolunteer, feedback, grade):
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
        "language": language,
        "language_level": language_level,
        "cientificResearch": cientificResearch,
        "companyName": companyName,
        "companyOccupation": companyOccupation,
        "companyDescription": companyDescription,
        "companyStartEnd": companyStartEnd,
        "companyNameVolunteer": companyNameVolunteer,
        "companyOccupationVolunteer": companyOccupationVolunteer,
        "companyDescriptionVolunteer": companyDescriptionVolunteer,
        "companyStartEndVolunteer": companyStartEndVolunteer,
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

    return response
    print(response.status_code)



# DADOS BASICOS FORM VERIFICAÇÃO 2.0
class ValidateDadosBasicosForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_curriculo_form"

    async def validate_nome(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do nome e primeiro nome """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
            nome_anterior = [] # lista que vai receber indices com primeira letra maisuscula
            preposicao = ['da', 'de', 'di', 'do', 'du'] # preposição  
    
            # verifica se cada item está na lista de preposições, se não estiver então transforma em maiúsculo. 
            # E por fim adiciona o item maiúsculo na nova lista chamada nome_anterior.
            for nome in value.split():
                if not nome in preposicao:
                    nome = nome.capitalize()
                nome_anterior.append(nome)

            # com o comando join() junto os items e coloco um espaço entre eles.
            novo_nome = ' '.join(nome_anterior)
            primeiro_nome = novo_nome.split()[0]

            return {"nome": novo_nome, "primeiroNome": primeiro_nome}
        else: 
            dispatcher.utter_message("Desculpa, não entendi.")
            return {"nome": None}

    async def validate_idade(self,
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

    async def validate_telefone(
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


    async def validate_cep(
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
        #     return {"endereco": "Brasilia", "cidade": "Brasília", "estado": "DF", "cep": value}
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


    async def validate_email(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando email com RE """

        # validando email com RE
        if re.findall(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", value):
            # requisição no banco pra verificação se já está cadastrado
            get_data_user = requests.get('http://curvi-api.herokuapp.com/api/user', headers={'email' : '{}'.format(value)})

            if get_data_user.status_code == 200:
                # 200 - conexão sucedida
                # 404 - not found
                # 500 - server
                
                # RECEBENDO DADOS DO BANCO EM JSON
                user_data = get_data_user.json()
                # print(user_data['name'], ", JÁ TE CONHEÇO...")
                dia_criado = user_data['created_at']

                dispatcher.utter_message("Acho que já nos conhecemos hein! Vi que você criou teu currículo no dia, {}. Esse email já está cadastrado e não é possível criarmos outro currículo. Só se quiser inserir outro...".format(dia_criado))
                return {"email": None}

            else:
                # status code diferente de 200, email disponível pra continuar
                return {"email": value.lower()}
        
        # email inválido pelo RE
        else:    
            dispatcher.utter_message("Email inválido...")
            return {"email": None}        


    async def validate_confirmacao_dados_basicos(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação dos dados básicos """

        confirmacao = tracker.get_slot("confirmacao_dados_basicos")
        if confirmacao == 'Sim':
            # se estiver certo, fluxo continua
            return {"confirmacao_dados_basicos": confirmacao}
        else:
            # se dados estiverem errados, slots setados pra None e fluxo é perguntado novamente.
            return {"nome": None, "idade": None, "cep": None, "cidade": None, "estado": None, "telefone": None, "email": None, "confirmacao_dados_basicos": None}



    # ======================= LINKEDIN =======================
    async def validate_user_has_linkedln(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do linkedin """

        confirmacao = tracker.get_slot("user_has_linkedln")
        if confirmacao == 'Sim':
            # se estiver certo, fluxo continua
            return {"user_has_linkedln": confirmacao}
        else:
            # se nao tiver linkedin, variáveis recebem not_print
            dispatcher.utter_message(template="utter_not_linkedln")
            return {"linkedln_link": "NOT_PRINT", "confirmacao_linkedln": 'NOT_PRINT', "user_has_linkedln": 'NOT_PRINT'}


    async def validate_linkedln_link(
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

    async def validate_confirmacao_linkedln(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação se link está certo """

        confirmacao = tracker.get_slot("confirmacao_linkedln")

        if confirmacao == 'Sim':
            return {"confirmacao_linkedln": confirmacao}
        else:
            return {"linkedln_link": None, "confirmacao_linkedln": None}


    #  ======================= FORMACAO FORM =======================
    async def validate_area(
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

        # Opção habilitada na escolha de botões, se nenhum for clicado, aceitar campo não vazio
        if value != '':
            return {"area": value}
        else:
            dispatcher.utter_message("Campo não pode ficar vazio.")
            return {"area": None}


    async def validate_area_nivel(
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
        
        # Opção habilitada na escolha de botões, se nenhum for clicado, aceitar campo não vazio
        if value != '':
            return {"area_nivel": value}
        else:
            dispatcher.utter_message("Campo não pode ficar vazio.")
            return {"area_nivel": None}


    async def validate_objetivo(
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


    async def validate_escolaridade(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando escolaridade """

        # Opção habilitada na escolha de botões, se nenhum for clicado, aceitar campo não vazio
        if value != '':
            return {"escolaridade": value}
        else:
            dispatcher.utter_message("Sua escolaridade é importante.")
            return {"escolaridade": None}


    async def validate_escolaridade_formadoOuAndamento(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando escolaridade_formadoOuAndamento """

        # verificando se o status é Completo ou Andamento
        status_escolaridade = tracker.get_slot("escolaridade_formadoOuAndamento")

        if value != '' and status_escolaridade == 'Completo':
            return {"escolaridade_formadoOuAndamento": value, "previsaoTermino": value}
        else:
            dispatcher.utter_message("O status é importante.")
            return {"escolaridade_formadoOuAndamento": None}

    
    async def validate_cursoNome(self,
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


    async def validate_institutoNome(self,
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


    async def validate_previsaoTermino(self,
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


    async def validate_confirmacao_formacao(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação da formação """

        confirmacao = tracker.get_slot("confirmacao_formacao")

        if confirmacao == 'Sim':
            return {"confirmacao_formacao": confirmacao}
        else:
            return {"area": None, "area_nivel": None, "objetivo": None, "escolaridade": None, "escolaridade_formadoOuAndamento": None, "cursoNome": None, "institutoNome": None, "previsaoTermino": None, "confirmacao_formacao": None}



    #  ======================= CURSO FORM =======================
    async def validate_conhecer_curso(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do curso """

        confirmacao = tracker.get_slot("conhecer_curso")

        if confirmacao == 'Sim':
            return {"conhecer_curso": confirmacao}
        else:
            # se nao tiver curso, recebe not_print e printa utter_not_habilidade
            dispatcher.utter_message(template="utter_not_habilidade")
            return {"habilidade": "NOT_PRINT", "confirmacao_habilidade": "NOT_PRINT", "conhecer_curso": "NOT_PRINT"}
        
    async def validate_habilidade(
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


    async def validate_confirmacao_habilidade(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação dos cursos """

        confirmacao = tracker.get_slot("confirmacao_habilidade")

        if confirmacao == 'Sim':
            return {"confirmacao_habilidade": confirmacao}
        else:
            return {"habilidade": None, "confirmacao_habilidade": None}



    #  ======================= IDIOMA FORM  =======================
    async def validate_conhecer_idioma(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do idioma """

        confirmacao = tracker.get_slot("conhecer_idioma")

        if confirmacao == 'Sim':
            return {"conhecer_idioma": confirmacao}
        else:
            # se nao tiver, recebe not_print
            dispatcher.utter_message(template="utter_not_idioma")
            return {"conhecer_idioma": "NOT_PRINT", "idioma": "NOT_PRINT", "idioma_nivel": "NOT_PRINT", "confirmacao_idioma": "NOT_PRINT"}

    async def validate_idioma(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando idioma """

        if value != '':
            return {"idioma": value}
        else:
            dispatcher.utter_message("Não entendi seu idioma, escreve de novo...")
            return {"idioma": None}

    async def validate_idioma_nivel(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando nível do idioma """

        if value != '':
            return {"idioma_nivel": value}
        else:
            dispatcher.utter_message("Não entendi seu nível...")
            return {"idioma_nivel": None}

    async def validate_confirmacao_idioma(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando confirmação do idioma """

        confirmacao = tracker.get_slot("confirmacao_idioma")
        if confirmacao == "Sim":
            return {"confirmacao_idioma": value}
        else:
            return {"idioma": None, "idioma_nivel": None, "confirmacao_idioma": None}



    #  ======================= PROJETOS E PESQUISAS CIENTIFICAS =======================
    async def validate_conhecer_projeto(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do projeto """

        confirmacao = tracker.get_slot("conhecer_projeto")

        if confirmacao == 'Sim':
            return {"conhecer_projeto": confirmacao}
        else:
            # se nao tiver, recebe not_print
            return {"conhecer_projeto": "NOT_PRINT", "pesquisaCientifica": "NOT_PRINT", "confirmacao_pesquisa": "NOT_PRINT"}

    async def validate_pesquisaCientifica(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação da pesquisa, aceitando texto """

        if value != '':
            return {"pesquisaCientifica": value}
        else:
            dispatcher.utter_message("Não entendi, vamos de novo...")
            return {"pesquisaCientifica": None}


    async def validate_confirmacao_pesquisa(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação da pesquisa, se tá correto ou não """

        confirmacao = tracker.get_slot("confirmacao_pesquisa")

        if confirmacao == 'Sim':
            return {"confirmacao_pesquisa": value}
        else:
            return {"pesquisaCientifica": None, "confirmacao_pesquisa": None}


    #  ======================= EXPERIENCIA FORM =======================
    async def validate_conhecer_experiencia(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do experiencia """

        confirmacao = tracker.get_slot("conhecer_experiencia")

        if confirmacao == 'Sim':
            return {"conhecer_experiencia": value}
        else:
            return {"cargo": "NOT_PRINT", "nomeEmpresa": "NOT_PRINT", "cargo_data_entrada_saida": "NOT_PRINT", "cargo_descricao": "NOT_PRINT", "confirmacao_experiencia": "NOT_PRINT", "conhecer_experiencia": "NOT_PRINT"}

    async def validate_cargo(self,
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


    async def validate_nomeEmpresa(self,
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

    
    async def validate_cargo_data_entrada_saida(self,
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


    async def validate_cargo_descricao(
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

    async def validate_confirmacao_experiencia(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação da experiência """

        confirmacao = tracker.get_slot("confirmacao_experiencia")
        if confirmacao == 'Sim':
            return {"confirmacao_experiencia": confirmacao}
        else:
            return {"cargo": None, "nomeEmpresa": None, "cargo_data_entrada_saida": None, "cargo_descricao": None, "confirmacao_experiencia": None}



    #  ======================= VOLUNTÁRIO FORM =======================
    async def validate_conhecer_voluntario(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do voluntário """

        confirmacao = tracker.get_slot("conhecer_voluntario")

        if confirmacao == 'Sim':
            return {"conhecer_voluntario": value}
        else:
            # se nao tiver, recebe not_print
            return {"conhecer_voluntario": "NOT_PRINT", "nome_empresa_voluntario": "NOT_PRINT", "cargo_voluntario": "NOT_PRINT", "cargo_descricao_voluntario": "NOT_PRINT", "cargo_data_entrada_saida_voluntario": "NOT_PRINT", "confirmacao_experiencia_voluntario": "NOT_PRINT"}

    async def validate_nome_empresa_voluntario(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando nome da empresa """

        # diferente de vazio
        if value != '':
            return {"nome_empresa_voluntario": value.capitalize(), "cargo_voluntario": "Voluntário"}
        else: 
            dispatcher.utter_message("Não entendi o nome da empresa. Me fala de novo... ")
            return {"nome_empresa_voluntario": None}


    async def validate_cargo_voluntario(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando cargo voluntário """

        # diferente de vazio
        if value != '':
            return {"cargo_voluntario": value.capitalize()}
        else: 
            dispatcher.utter_message("Não entendi seu cargo. Vamos de novo! ")
            return {"cargo_voluntario": None}

    
    async def validate_cargo_data_entrada_saida_voluntario(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando saída do emprego """

        if value != '':
            return {"cargo_data_entrada_saida_voluntario": value}
        else:
            dispatcher.utter_message("Não entendi...")
            return {"cargo_data_entrada_saida_voluntario": None}


    async def validate_cargo_descricao_voluntario(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando descrição do cargo """

        # diferente de vazio
        if value != '':
            return {"cargo_descricao_voluntario": value.capitalize()}
        else: 
            dispatcher.utter_message("Me fala de novo, não entendi... ")
            return {"cargo_descricao_voluntario": None}

    async def validate_confirmacao_experiencia_voluntario(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação da experiência """

        confirmacao = tracker.get_slot("confirmacao_experiencia_voluntario")
        if confirmacao == 'Sim':
            return {"confirmacao_experiencia_voluntario": confirmacao}
        else:
            return {"cargo_voluntario": None, "nome_empresa_voluntario": None, "cargo_data_entrada_saida_voluntario": None, "cargo_descricao_voluntario": None, "confirmacao_experiencia_voluntario": None}



    #  ======================= FEEDBACK FORM ============================
    async def validate_feedback(
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


    async def validate_nota(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando nota """

        # campo não vazio, única verificação
        if value != '':
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

        language = tracker.get_slot("idioma")
        if language == None:
            language = "NOT_PRINT"
        language_level = tracker.get_slot("idioma_nivel")

        cientificResearch = tracker.get_slot("pesquisaCientifica")
        if cientificResearch == None:
            cientificResearch = "NOT_PRINT"

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


        companyNameVolunteer = tracker.get_slot("nome_empresa_voluntario")
        if companyNameVolunteer == None:
            companyNameVolunteer = "Primeiro emprego objetivando adquirir conhecimento e experiência necessária junto à empresa."

        companyOccupationVolunteer = tracker.get_slot("cargo_voluntario")
        if companyOccupationVolunteer == None:
            companyOccupationVolunteer = "NOT_PRINT"

        companyDescriptionVolunteer = tracker.get_slot("cargo_descricao_voluntario")
        if companyDescriptionVolunteer == None:
            companyDescriptionVolunteer = "NOT_PRINT"

        companyStartEndVolunteer = tracker.get_slot("cargo_data_entrada_saida_voluntario")
        if companyStartEnd == None:
            companyStartEnd = "NOT_PRINT"

        feedback = tracker.get_slot("feedback")
        grade = tracker.get_slot("nota")
        

        # CHAMADA DA FUNÇÃO PASSANDO OS DADOS PRA FAZER POST REQUEST
        generate_pdf(name, age, address, city, state, cellphone, email, linkedln_link, area, area_level, goal, scholarity, 
                courseName, courseSchool, courseEndYear, courses, language, language_level, cientificResearch, companyName, 
                companyOccupation, companyDescription, companyStartEnd, companyNameVolunteer, companyOccupationVolunteer,
                companyDescriptionVolunteer, companyStartEndVolunteer, feedback, grade)


        # após post request, zerando todos os slots para None
        return [
            SlotSet("nome", None),
            SlotSet("primeiroNome", None),
            SlotSet("idade", None),
            SlotSet("cep", None),
            SlotSet("endereco", None),
            SlotSet("cidade", None),
            SlotSet("estado", None),
            SlotSet("telefone", None),
            SlotSet("email", None),
            SlotSet("linkedln_link", None),
            SlotSet("user_has_linkedln", None),
            SlotSet("area", None),
            SlotSet("area_nivel", None),
            SlotSet("objetivo", None),
            SlotSet("escolaridade", None),
            SlotSet("escolaridade_formadoOuAndamento", None),
            SlotSet("cursoNome", None),
            SlotSet("institutoNome", None),
            SlotSet("previsaoTermino", None),
            SlotSet("conhecer_curso", None),
            SlotSet("habilidade", None),
            SlotSet("conhecer_idioma", None),
            SlotSet("idioma", None),
            SlotSet("idioma_nivel", None),
            SlotSet("conhecer_projeto", None),
            SlotSet("pesquisaCientifica", None),
            SlotSet("conhecer_experiencia", None),
            SlotSet("nomeEmpresa", None),
            SlotSet("cargo", None),
            SlotSet("cargo_descricao", None),
            SlotSet("cargo_data_entrada_saida", None),
            SlotSet("conhecer_voluntario", None),
            SlotSet("nome_empresa_voluntario", None),
            SlotSet("cargo_voluntario", None),
            SlotSet("cargo_descricao_voluntario", None),
            SlotSet("cargo_data_entrada_saida_voluntario", None),
            SlotSet("feedback", None),
            SlotSet("nota", None),
            SlotSet("confirmacao_dados_basicos", None),
            SlotSet("confirmacao_formacao", None),
            SlotSet("confirmacao_habilidade", None),
            SlotSet("confirmacao_pesquisa", None),
            SlotSet("confirmacao_experiencia", None),
            SlotSet("confirmacao_linkedln", None),
            SlotSet("confirmacao_experiencia_voluntario", None),
            SlotSet("confirmacao_idioma", None)
        ]

        # dispatcher.utter_message("")