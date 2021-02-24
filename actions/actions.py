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
        "9_email": email,
        "12_linkedln_link": linkedln_link,
        "14_area": area,
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
        "46_feedback": feedback,
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

    async def validate_1_nome(self,
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

            return {"1_nome": novo_nome, "2_primeiroNome": primeiro_nome}
        else: 
            dispatcher.utter_message("Desculpa, não entendi.")
            return {"1_nome": None}

    async def validate_3_idade(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do idade """

        # conter apenas números
        if value.isdigit() and int(value) > 0 and int(value) < 100:
            return {"3_idade": value}
        else: 
            dispatcher.utter_message("Apenas número...")
            return {"3_idade": None}

    async def validate_8_telefone(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validação do telefone """

        # verificando se é número e se contém 11 dígitos númericos
        if value.isdigit() and len(value) == 11:
            return {"8_telefone": value}
        else:
            dispatcher.utter_message("Não entendi. Insira apenas o DDD seguido do número.")
            return {"8_telefone": None}


    async def validate_4_cep(
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
                return {"4_cep": None}

            # se for válido, printa endereço
            else:
                # pegar valor do endereco
                endereco = tracker.get_slot("6_endereco")

                # endereço recebe o valor vindo da chamada da API
                endereco = address['logradouro']
                bairro = address['bairro']
                localidade = address['localidade']
                uf = address['uf']
                
                # printando mensagem após endereço encontrado
                dispatcher.utter_message("Vi que seu endereço é: {}, {}, {} - {} \n".format(endereco, bairro, localidade, uf))
                
                # retornando slots com valores preenchidos
                return {"6_endereco": endereco, "5_cidade": localidade, "7_estado": uf, "4_cep": cep}
        
        # printar erro se não tiver 8 dígitos
        else:
            dispatcher.utter_message("CEP inválido, vamos de novo.")
            return {"4_cep": None}


    async def validate_9_email(
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
                return {"9_email": None}

            else:
                # status code diferente de 200, email disponível pra continuar
                return {"9_email": value.lower()}
        
        # email inválido pelo RE
        else:    
            dispatcher.utter_message("Email inválido...")
            return {"9_email": None}        


    async def validate_10_confirmacao_dados_basicos(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação dos dados básicos """

        confirmacao = tracker.get_slot("10_confirmacao_dados_basicos")
        if confirmacao == 'Sim':
            # se estiver certo, fluxo continua
            return {"10_confirmacao_dados_basicos": confirmacao}
        else:
            # se dados estiverem errados, slots setados pra None e fluxo é perguntado novamente.
            return {"1_nome": None, "3_idade": None, "4_cep": None, "5_cidade": None, "7_estado": None, "8_telefone": None, "9_email": None, "10_confirmacao_dados_basicos": None}



    # ======================= LINKEDIN =======================
    async def validate_11_user_has_linkedln(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do linkedin """

        confirmacao = tracker.get_slot("11_user_has_linkedln")
        if confirmacao == 'Sim':
            # se estiver certo, fluxo continua
            return {"11_user_has_linkedln": confirmacao}
        else:
            # se nao tiver linkedin, variáveis recebem not_print
            dispatcher.utter_message(template="utter_not_linkedln")
            return {"12_linkedln_link": "NOT_PRINT", "13_confirmacao_linkedln": 'NOT_PRINT', "11_user_has_linkedln": 'NOT_PRINT'}


    async def validate_12_linkedln_link(
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
            return {"12_linkedln_link": value.lower()}
        else: 
            # dispatcher.utter_message("Vamos de novo! ")
            return {"12_linkedln_link": None}

    async def validate_13_confirmacao_linkedln(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação se link está certo """

        confirmacao = tracker.get_slot("13_confirmacao_linkedln")

        if confirmacao == 'Sim':
            return {"13_confirmacao_linkedln": confirmacao}
        else:
            return {"12_linkedln_link": None, "13_confirmacao_linkedln": None}


    #  ======================= FORMACAO FORM =======================
    async def validate_14_area(
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
            return {"14_area": value}
        else:
            dispatcher.utter_message("Campo não pode ficar vazio.")
            return {"14_area": None}


    async def validate_15_area_nivel(
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
            return {"15_area_nivel": value}
        else:
            dispatcher.utter_message("Campo não pode ficar vazio.")
            return {"15_area_nivel": None}


    async def validate_21_objetivo(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando 21_objetivo """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        # if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
        if value != '':
            # slot recebe valor inserido devidamente aprovado pelo regular expressions
            return {"21_objetivo": value.capitalize()}
        else: 
            dispatcher.utter_message("Vamos de novo! ")
            return {"21_objetivo": None}


    async def validate_16_escolaridade(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando escolaridade """

        # Opção habilitada na escolha de botões, se nenhum for clicado, aceitar campo não vazio
        if value != '':
            return {"16_escolaridade": value}
        else:
            dispatcher.utter_message("Sua escolaridade é importante.")
            return {"16_escolaridade": None}


    async def validate_17_escolaridadeFormadoOuAndamento(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando escolaridadeFormadoOuAndamento """

        # verificando se o status é Completo ou Andamento
        status_escolaridade = tracker.get_slot("17_escolaridadeFormadoOuAndamento")

        if status_escolaridade == 'Completo':
            return {"17_escolaridadeFormadoOuAndamento": value, "20_previsaoTermino": value}
        else:
            return {"17_escolaridadeFormadoOuAndamento": "Em andamento"}

    
    async def validate_18_cursoNome(self,
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
            return {"18_cursoNome": value}
        else: 
            dispatcher.utter_message("Vamos de novo! ")
            return {"18_cursoNome": None}


    async def validate_19_institutoNome(self,
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
            return {"19_institutoNome": value}
        else: 
            dispatcher.utter_message("Vamos de novo! ")
            return {"19_institutoNome": None}


    async def validate_20_previsaoTermino(self,
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
                return {"20_previsaoTermino": value}
            else:
                dispatcher.utter_message("Somente o ano! Lembre-se que você só pode terminar o curso esse ano, {}, em diante...".format(ano_atual))
                return {"20_previsaoTermino": None}
        else:
            dispatcher.utter_message("Não entendi...")
            return {"20_previsaoTermino": None}


    async def validate_22_confirmacao_formacao(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação da formação """

        confirmacao = tracker.get_slot("22_confirmacao_formacao")

        if confirmacao == 'Sim':
            return {"22_confirmacao_formacao": confirmacao}
        else:
            return {"14_area": None, "15_area_nivel": None, "21_objetivo": None, "16_escolaridade": None, "17_escolaridadeFormadoOuAndamento": None, "18_cursoNome": None, "19_institutoNome": None, "20_previsaoTermino": None, "22_confirmacao_formacao": None}



    #  ======================= CURSO FORM =======================
    async def validate_23_conhecer_curso(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do curso """

        confirmacao = tracker.get_slot("23_conhecer_curso")

        if confirmacao == 'Sim':
            return {"23_conhecer_curso": confirmacao}
        else:
            # se nao tiver curso, recebe not_print e printa utter_not_habilidade
            dispatcher.utter_message(template="utter_not_habilidade")
            return {"24_habilidade": "NOT_PRINT", "25_confirmacao_habilidade": "NOT_PRINT", "23_conhecer_curso": "NOT_PRINT"}
        
    async def validate_24_habilidade(
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
            return {"24_habilidade": value.capitalize()}
        else: 
            dispatcher.utter_message("Me fala de novo quais cursos você possui, não entendi... ")
            return {"24_habilidade": None}


    async def validate_25_confirmacao_habilidade(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação dos cursos """

        confirmacao = tracker.get_slot("25_confirmacao_habilidade")

        if confirmacao == 'Sim':
            return {"25_confirmacao_habilidade": confirmacao}
        else:
            return {"24_habilidade": None, "25_confirmacao_habilidade": None}



    #  ======================= IDIOMA FORM  =======================
    async def validate_26_conhecer_idioma(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do idioma """

        confirmacao = tracker.get_slot("26_conhecer_idioma")

        if confirmacao == 'Sim':
            return {"26_conhecer_idioma": confirmacao}
        else:
            # se nao tiver, recebe not_print
            dispatcher.utter_message(template="utter_not_idioma")
            return {"26_conhecer_idioma": "NOT_PRINT", "27_idioma": "NOT_PRINT", "28_idioma_nivel": "NOT_PRINT", "29_confirmacao_idioma": "NOT_PRINT"}

    async def validate_27_idioma(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando idioma """

        if value != '':
            return {"27_idioma": value}
        else:
            dispatcher.utter_message("Não entendi seu idioma, escreve de novo...")
            return {"27_idioma": None}

    async def validate_28_idioma_nivel(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando nível do idioma """

        if value != '':
            return {"28_idioma_nivel": value}
        else:
            dispatcher.utter_message("Não entendi seu nível...")
            return {"28_idioma_nivel": None}

    async def validate_29_confirmacao_idioma(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando confirmação do idioma """

        confirmacao = tracker.get_slot("29_confirmacao_idioma")
        if confirmacao == "Sim":
            return {"29_confirmacao_idioma": value}
        else:
            return {"27_idioma": None, "28_idioma_nivel": None, "29_confirmacao_idioma": None}



    #  ======================= PROJETOS E PESQUISAS CIENTIFICAS =======================
    async def validate_30_conhecer_projeto(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do projeto """

        confirmacao = tracker.get_slot("30_conhecer_projeto")

        if confirmacao == 'Sim':
            return {"30_conhecer_projeto": confirmacao}
        else:
            # se nao tiver, recebe not_print
            return {"30_conhecer_projeto": "NOT_PRINT", "31_pesquisaCientifica": "NOT_PRINT", "32_confirmacao_pesquisa": "NOT_PRINT"}

    async def validate_31_pesquisaCientifica(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação da pesquisa, aceitando texto """

        if value != '':
            return {"31_pesquisaCientifica": value}
        else:
            dispatcher.utter_message("Não entendi, vamos de novo...")
            return {"31_pesquisaCientifica": None}


    async def validate_32_confirmacao_pesquisa(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação da pesquisa, se tá correto ou não """

        confirmacao = tracker.get_slot("32_confirmacao_pesquisa")

        if confirmacao == 'Sim':
            return {"32_confirmacao_pesquisa": value}
        else:
            return {"31_pesquisaCientifica": None, "32_confirmacao_pesquisa": None}


    #  ======================= EXPERIENCIA FORM =======================
    async def validate_33_conhecer_experiencia(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do experiencia """

        confirmacao = tracker.get_slot("33_conhecer_experiencia")

        if confirmacao == 'Sim':
            # se tiver experiencia, segue o fluxo e não pergunta sobre curso online
            return {"33_conhecer_experiencia": value, "34_curso_online":"nao"}
        else:
            return {"36_cargo": "NOT_PRINT", "35_nomeEmpresa": "NOT_PRINT", "38_cargo_data_entrada_saida": "NOT_PRINT", "37_cargo_descricao": "NOT_PRINT", "39_confirmacao_experiencia": "NOT_PRINT", "33_conhecer_experiencia": "NOT_PRINT"}


    async def validate_34_curso_online(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando curso_online """

        confirmacao = tracker.get_slot("34_curso_online")
        if confirmacao == 'sim':
            # envia link do curso gratuito caso usuário nao tenha experiência
            dispatcher.utter_message(template="utter_curso_online_link")
            return {"34_curso_online": value}
        else: 
            dispatcher.utter_message("Ok, continuando então... ")
            return {"34_curso_online": "nao"}


    async def validate_36_cargo(self,
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
            return {"36_cargo": value.capitalize()}
        else: 
            dispatcher.utter_message("Não entendi seu cargo. Vamos de novo! ")
            return {"36_cargo": None}


    async def validate_35_nomeEmpresa(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando nome da empresa """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        # if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
        if value != '':
            return {"35_nomeEmpresa": value.capitalize()}
        else: 
            dispatcher.utter_message("Não entendi o nome da empresa. Me fala de novo... ")
            return {"35_nomeEmpresa": None}

    
    async def validate_38_cargo_data_entrada_saida(self,
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
            return {"38_cargo_data_entrada_saida": value}
        else:
            dispatcher.utter_message("Não entendi...")
            return {"38_cargo_data_entrada_saida": None}


    async def validate_37_cargo_descricao(
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
            return {"37_cargo_descricao": value.capitalize()}
        else: 
            dispatcher.utter_message("Me fala de novo, não entendi... ")
            return {"37_cargo_descricao": None}

    async def validate_39_confirmacao_experiencia(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação da experiência """

        confirmacao = tracker.get_slot("39_confirmacao_experiencia")
        if confirmacao == 'Sim':
            return {"39_confirmacao_experiencia": confirmacao}
        else:
            return {"36_cargo": None, "35_nomeEmpresa": None, "38_cargo_data_entrada_saida": None, "37_cargo_descricao": None, "39_confirmacao_experiencia": None}



    #  ======================= VOLUNTÁRIO FORM =======================
    async def validate_40_conhecer_voluntario(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do voluntário """

        confirmacao = tracker.get_slot("40_conhecer_voluntario")

        if confirmacao == 'Sim':
            return {"40_conhecer_voluntario": value}
        else:
            # se nao tiver, recebe not_print
            return {"40_conhecer_voluntario": "NOT_PRINT", "41_nome_empresa_voluntario": "NOT_PRINT", "42_cargo_voluntario": "NOT_PRINT", "43_cargo_descricao_voluntario": "NOT_PRINT", "44_cargo_data_entrada_saida_voluntario": "NOT_PRINT", "45_confirmacao_experiencia_voluntario": "NOT_PRINT"}

    async def validate_41_nome_empresa_voluntario(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando nome da empresa """

        # diferente de vazio
        if value != '':
            return {"41_nome_empresa_voluntario": value.capitalize(), "42_cargo_voluntario": "Voluntário"}
        else: 
            dispatcher.utter_message("Não entendi o nome da empresa. Me fala de novo... ")
            return {"41_nome_empresa_voluntario": None}


    async def validate_42_cargo_voluntario(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando cargo voluntário """

        # diferente de vazio
        if value != '':
            return {"42_cargo_voluntario": value.capitalize()}
        else: 
            dispatcher.utter_message("Não entendi seu cargo. Vamos de novo! ")
            return {"42_cargo_voluntario": None}

    
    async def validate_44_cargo_data_entrada_saida_voluntario(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando saída do emprego """

        if value != '':
            return {"44_cargo_data_entrada_saida_voluntario": value}
        else:
            dispatcher.utter_message("Não entendi...")
            return {"44_cargo_data_entrada_saida_voluntario": None}


    async def validate_43_cargo_descricao_voluntario(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando descrição do cargo """

        # diferente de vazio
        if value != '':
            return {"43_cargo_descricao_voluntario": value.capitalize()}
        else: 
            dispatcher.utter_message("Me fala de novo, não entendi... ")
            return {"43_cargo_descricao_voluntario": None}

    async def validate_45_confirmacao_experiencia_voluntario(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação da experiência """

        confirmacao = tracker.get_slot("45_confirmacao_experiencia_voluntario")
        if confirmacao == 'Sim':
            return {"45_confirmacao_experiencia_voluntario": confirmacao}
        else:
            return {"42_cargo_voluntario": None, "41_nome_empresa_voluntario": None, "44_cargo_data_entrada_saida_voluntario": None, "43_cargo_descricao_voluntario": None, "45_confirmacao_experiencia_voluntario": None}



    #  ======================= FEEDBACK FORM ============================
    async def validate_46_feedback(
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
            return {"46_feedback": value}
        else: 
            dispatcher.utter_message("Vamos de novo... ")
            return {"46_feedback": None}


    async def validate_47_nota(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando 47_nota """

        # campo não vazio, única verificação
        if value != '':
            return {"47_nota": value}
        else: 
            dispatcher.utter_message("Vamos de novo... ")
            return {"47_nota": None}






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
        name = tracker.get_slot("1_nome")
        age = tracker.get_slot("3_idade")
        address = tracker.get_slot("6_endereco")
        city = tracker.get_slot("5_cidade")
        state = tracker.get_slot("7_estado")
        cellphone = tracker.get_slot("8_telefone")
        email = tracker.get_slot("9_email")

        linkedln_link = tracker.get_slot("12_linkedln_link")
        if linkedln_link == None:
            linkedln_link = "NOT_PRINT"

        area = tracker.get_slot("14_area")
        area_level = tracker.get_slot("15_area_nivel")
        goal = tracker.get_slot("21_objetivo")
        scholarity = tracker.get_slot("16_escolaridade")
        courseName = tracker.get_slot("18_cursoNome")
        courseSchool = tracker.get_slot("19_institutoNome")
        courseEndYear = tracker.get_slot("20_previsaoTermino")

        courses = tracker.get_slot("24_habilidade")
        if courses == None:
            courses = "NOT_PRINT"

        language = tracker.get_slot("27_idioma")
        if language == None:
            language = "NOT_PRINT"
        language_level = tracker.get_slot("28_idioma_nivel")

        cientificResearch = tracker.get_slot("31_pesquisaCientifica")
        if cientificResearch == None:
            cientificResearch = "NOT_PRINT"

        companyName = tracker.get_slot("35_nomeEmpresa")
        if companyName == None:
            companyName = "Primeiro emprego objetivando adquirir conhecimento e experiência necessária junto à empresa."

        companyOccupation = tracker.get_slot("36_cargo")
        if companyOccupation == None:
            companyOccupation = "NOT_PRINT"

        companyDescription = tracker.get_slot("37_cargo_descricao")
        if companyDescription == None:
            companyDescription = "NOT_PRINT"

        companyStartEnd = tracker.get_slot("38_cargo_data_entrada_saida")
        if companyStartEnd == None:
            companyStartEnd = "NOT_PRINT"


        companyNameVolunteer = tracker.get_slot("41_nome_empresa_voluntario")
        if companyNameVolunteer == None:
            companyNameVolunteer = "Primeiro emprego objetivando adquirir conhecimento e experiência necessária junto à empresa."

        companyOccupationVolunteer = tracker.get_slot("42_cargo_voluntario")
        if companyOccupationVolunteer == None:
            companyOccupationVolunteer = "NOT_PRINT"

        companyDescriptionVolunteer = tracker.get_slot("43_cargo_descricao_voluntario")
        if companyDescriptionVolunteer == None:
            companyDescriptionVolunteer = "NOT_PRINT"

        companyStartEndVolunteer = tracker.get_slot("44_cargo_data_entrada_saida_voluntario")
        if companyStartEnd == None:
            companyStartEnd = "NOT_PRINT"

        feedback = tracker.get_slot("46_feedback")
        grade = tracker.get_slot("47_nota")
        

        # CHAMADA DA FUNÇÃO PASSANDO OS DADOS PRA FAZER POST REQUEST
        # generate_pdf(name, age, address, city, state, cellphone, email, linkedln_link, area, area_level, goal, scholarity, 
        #         courseName, courseSchool, courseEndYear, courses, language, language_level, cientificResearch, companyName, 
        #         companyOccupation, companyDescription, companyStartEnd, companyNameVolunteer, companyOccupationVolunteer,
        #         companyDescriptionVolunteer, companyStartEndVolunteer, feedback, grade)


        # após post request, zerando todos os slots para None
        return [
            SlotSet("1_nome", None),
            SlotSet("2_primeiroNome", None),
            SlotSet("3_idade", None),
            SlotSet("4_cep", None),
            SlotSet("5_cidade", None),
            SlotSet("6_endereco", None),            
            SlotSet("7_estado", None),
            SlotSet("8_telefone", None),
            SlotSet("9_email", None),
            SlotSet("10_confirmacao_dados_basicos", None),
            SlotSet("11_user_has_linkedln", None),
            SlotSet("12_linkedln_link", None),
            SlotSet("13_confirmacao_linkedln", None),
            SlotSet("14_area", None),
            SlotSet("15_area_nivel", None),
            SlotSet("16_escolaridade", None),
            SlotSet("17_escolaridadeFormadoOuAndamento", None),
            SlotSet("18_cursoNome", None),
            SlotSet("19_institutoNome", None),
            SlotSet("20_previsaoTermino", None),
            SlotSet("21_objetivo", None),
            SlotSet("22_confirmacao_formacao", None),
            SlotSet("23_conhecer_curso", None),
            SlotSet("24_habilidade", None),
            SlotSet("25_confirmacao_habilidade", None),
            SlotSet("26_conhecer_idioma", None),
            SlotSet("27_idioma", None),
            SlotSet("28_idioma_nivel", None),
            SlotSet("29_confirmacao_idioma", None),      
            SlotSet("30_conhecer_projeto", None),
            SlotSet("31_pesquisaCientifica", None),
            SlotSet("32_confirmacao_pesquisa", None),
            SlotSet("33_conhecer_experiencia", None),
            SlotSet("34_curso_online", None),
            SlotSet("35_nomeEmpresa", None),
            SlotSet("36_cargo", None),
            SlotSet("37_cargo_descricao", None),
            SlotSet("38_cargo_data_entrada_saida", None),
            SlotSet("39_confirmacao_experiencia", None),
            SlotSet("40_conhecer_voluntario", None),
            SlotSet("41_nome_empresa_voluntario", None),
            SlotSet("42_cargo_voluntario", None),
            SlotSet("43_cargo_descricao_voluntario", None),
            SlotSet("44_cargo_data_entrada_saida_voluntario", None),
            SlotSet("45_confirmacao_experiencia_voluntario", None),
            SlotSet("46_feedback", None),
            SlotSet("47_nota", None),
        ]

        # dispatcher.utter_message("")