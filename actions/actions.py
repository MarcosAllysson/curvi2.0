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
    # request_url = "https://curvi-api.herokuapp.com/api/user"
    request_url = "https://sincere-quasar-301622.rj.r.appspot.com/api/user"

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

    async def validate_AA_nome(self,
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

            return {"AA_nome": novo_nome, "A_primeiroNome": primeiro_nome}
        else: 
            dispatcher.utter_message("Desculpa, não entendi.")
            return {"AA_nome": None}

    async def validate_B_idade(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do idade """

        # conter apenas números
        if value.isdigit() and int(value) > 0 and int(value) < 100:
            return {"B_idade": value}
        else: 
            dispatcher.utter_message("Apenas número...")
            return {"B_idade": None}

    async def validate_D_telefone(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validação do telefone """

        # verificando se é número e se contém 11 dígitos númericos
        if value.isdigit() and len(value) == 11:
            return {"D_telefone": value}
        else:
            dispatcher.utter_message("Não entendi. Insira apenas o DDD seguido do número.")
            return {"D_telefone": None}


    async def validate_CCCC_cep(
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
                return {"CCCC_cep": None}

            # se for válido, printa endereço
            else:
                # pegar valor do endereco
                endereco = tracker.get_slot("CC_endereco")

                # endereço recebe o valor vindo da chamada da API
                endereco = address['logradouro']
                bairro = address['bairro']
                localidade = address['localidade']
                uf = address['uf']
                
                # printando mensagem após endereço encontrado
                dispatcher.utter_message("Vi que seu endereço é: {}, {}, {} - {} \n".format(endereco, bairro, localidade, uf))
                
                # retornando slots com valores preenchidos
                return {"CC_endereco": endereco, "CCC_cidade": localidade, "C_estado": uf, "CCCC_cep": cep}
        
        # printar erro se não tiver 8 dígitos
        else:
            dispatcher.utter_message("CEP inválido, vamos de novo.")
            return {"CCCC_cep": None}


    async def validate_E_email(
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
            # get_data_user = requests.get('http://curvi-api.herokuapp.com/api/user', headers={'email' : '{}'.format(value)})
            get_data_user = requests.get('https://sincere-quasar-301622.rj.r.appspot.com/api/user', headers={'email' : '{}'.format(value)})

            if get_data_user.status_code == 200:
                # 200 - conexão sucedida
                # 404 - not found
                # 500 - server
                
                # RECEBENDO DADOS DO BANCO EM JSON
                user_data = get_data_user.json()
                # print(user_data['name'], ", JÁ TE CONHEÇO...")
                dia_criado = user_data['created_at']

                dispatcher.utter_message("Acho que já nos conhecemos hein! Vi que você criou teu currículo no dia, {}. Esse email já está cadastrado e não é possível criarmos outro currículo. Só se quiser inserir outro...".format(dia_criado))
                return {"E_email": None}

            else:
                # status code diferente de 200, email disponível pra continuar
                return {"E_email": value.lower()}
        
        # email inválido pelo RE
        else:    
            dispatcher.utter_message("Email inválido...")
            return {"E_email": None}        


    async def validate_F_confirmacao_dados_basicos(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação dos dados básicos """

        confirmacao = tracker.get_slot("F_confirmacao_dados_basicos")
        if confirmacao == 'Sim':
            # se estiver certo, fluxo continua
            return {"F_confirmacao_dados_basicos": confirmacao}
        else:
            # se dados estiverem errados, slots setados pra None e fluxo é perguntado novamente.
            return {"AA_nome": None, "B_idade": None, "CCCC_cep": None, "CCC_cidade": None, "C_estado": None, "D_telefone": None, "E_email": None, "F_confirmacao_dados_basicos": None}



    # ======================= LINKEDIN =======================
    async def validate_GGG_user_has_linkedln(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do linkedin """

        confirmacao = tracker.get_slot("GGG_user_has_linkedln")
        if confirmacao == 'Sim':
            # se estiver certo, fluxo continua
            return {"GGG_user_has_linkedln": confirmacao}
        else:
            # se nao tiver linkedin, variáveis recebem not_print
            dispatcher.utter_message(template="utter_not_linkedln")
            return {"GG_linkedln_link": "NOT_PRINT", "G_confirmacao_linkedln": 'NOT_PRINT', "GGG_user_has_linkedln": 'NOT_PRINT'}


    async def validate_GG_linkedln_link(
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
            return {"GG_linkedln_link": value.lower()}
        else: 
            # dispatcher.utter_message("Vamos de novo! ")
            return {"GG_linkedln_link": None}

    async def validate_G_confirmacao_linkedln(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação se link está certo """

        confirmacao = tracker.get_slot("G_confirmacao_linkedln")

        if confirmacao == 'Sim':
            return {"G_confirmacao_linkedln": confirmacao}
        else:
            return {"GG_linkedln_link": None, "G_confirmacao_linkedln": None}


    #  ======================= FORMACAO FORM =======================
    async def validate_HH_area(
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
            return {"HH_area": value}
        else:
            dispatcher.utter_message("Campo não pode ficar vazio.")
            return {"HH_area": None}


    async def validate_H_area_nivel(
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
            return {"H_area_nivel": value}
        else:
            dispatcher.utter_message("Campo não pode ficar vazio.")
            return {"H_area_nivel": None}


    async def validate_L_objetivo(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando L_objetivo """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        # if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
        if value != '':
            # slot recebe valor inserido devidamente aprovado pelo regular expressions
            return {"L_objetivo": value.capitalize()}
        else: 
            dispatcher.utter_message("Vamos de novo! ")
            return {"L_objetivo": None}


    async def validate_II_escolaridade(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando escolaridade """

        # Opção habilitada na escolha de botões, se nenhum for clicado, aceitar campo não vazio
        if value != '':
            return {"II_escolaridade": value}
        else:
            dispatcher.utter_message("Sua escolaridade é importante.")
            return {"II_escolaridade": None}


    async def validate_I_escolaridadeFormadoOuAndamento(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando escolaridadeFormadoOuAndamento """

        # verificando se o status é Completo ou Andamento
        status_escolaridade = tracker.get_slot("I_escolaridadeFormadoOuAndamento")

        if status_escolaridade == 'Completo':
            return {"I_escolaridadeFormadoOuAndamento": value, "K_previsaoTermino": value}
        else:
            return {"I_escolaridadeFormadoOuAndamento": "Em andamento"}

    
    async def validate_JJ_cursoNome(self,
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
            return {"JJ_cursoNome": value}
        else: 
            dispatcher.utter_message("Vamos de novo! ")
            return {"JJ_cursoNome": None}


    async def validate_J_institutoNome(self,
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
            return {"J_institutoNome": value}
        else: 
            dispatcher.utter_message("Vamos de novo! ")
            return {"J_institutoNome": None}


    async def validate_K_previsaoTermino(self,
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
                return {"K_previsaoTermino": value}
            else:
                dispatcher.utter_message("Somente o ano! Lembre-se que você só pode terminar o curso esse ano, {}, em diante...".format(ano_atual))
                return {"K_previsaoTermino": None}
        else:
            dispatcher.utter_message("Não entendi...")
            return {"K_previsaoTermino": None}


    async def validate_M_confirmacao_formacao(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação da formação """

        confirmacao = tracker.get_slot("M_confirmacao_formacao")

        if confirmacao == 'Sim':
            return {"M_confirmacao_formacao": confirmacao}
        else:
            return {"HH_area": None, "H_area_nivel": None, "L_objetivo": None, "II_escolaridade": None, "I_escolaridadeFormadoOuAndamento": None, "JJ_cursoNome": None, "J_institutoNome": None, "K_previsaoTermino": None, "M_confirmacao_formacao": None}



    #  ======================= CURSO FORM =======================
    async def validate_NNN_conhecer_curso(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do curso """

        confirmacao = tracker.get_slot("NNN_conhecer_curso")

        if confirmacao == 'Sim':
            return {"NNN_conhecer_curso": confirmacao}
        else:
            # se nao tiver curso, recebe not_print e printa utter_not_habilidade
            dispatcher.utter_message(template="utter_not_habilidade")
            return {"NN_habilidade": "NOT_PRINT", "N_confirmacao_habilidade": "NOT_PRINT", "NNN_conhecer_curso": "NOT_PRINT"}
        
    async def validate_NN_habilidade(
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
            return {"NN_habilidade": value.capitalize()}
        else: 
            dispatcher.utter_message("Me fala de novo quais cursos você possui, não entendi... ")
            return {"NN_habilidade": None}


    async def validate_N_confirmacao_habilidade(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação dos cursos """

        confirmacao = tracker.get_slot("N_confirmacao_habilidade")

        if confirmacao == 'Sim':
            return {"N_confirmacao_habilidade": confirmacao}
        else:
            return {"NN_habilidade": None, "N_confirmacao_habilidade": None}



    #  ======================= IDIOMA FORM  =======================
    async def validate_OOOO_conhecer_idioma(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do idioma """

        confirmacao = tracker.get_slot("OOOO_conhecer_idioma")

        if confirmacao == 'Sim':
            return {"OOOO_conhecer_idioma": confirmacao}
        else:
            # se nao tiver, recebe not_print
            dispatcher.utter_message(template="utter_not_idioma")
            return {"OOOO_conhecer_idioma": "NOT_PRINT", "OOO_idioma": "NOT_PRINT", "OO_idioma_nivel": "NOT_PRINT", "O_confirmacao_idioma": "NOT_PRINT"}

    async def validate_OOO_idioma(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando idioma """

        if value != '':
            return {"OOO_idioma": value}
        else:
            dispatcher.utter_message("Não entendi seu idioma, escreve de novo...")
            return {"OOO_idioma": None}

    async def validate_OO_idioma_nivel(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando nível do idioma """

        if value != '':
            return {"OO_idioma_nivel": value}
        else:
            dispatcher.utter_message("Não entendi seu nível...")
            return {"OO_idioma_nivel": None}

    async def validate_O_confirmacao_idioma(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando confirmação do idioma """

        confirmacao = tracker.get_slot("O_confirmacao_idioma")
        if confirmacao == "Sim":
            return {"O_confirmacao_idioma": value}
        else:
            return {"OOO_idioma": None, "OO_idioma_nivel": None, "O_confirmacao_idioma": None}



    #  ======================= PROJETOS E PESQUISAS CIENTIFICAS =======================
    async def validate_PP_conhecer_projeto(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do projeto """

        confirmacao = tracker.get_slot("PP_conhecer_projeto")

        if confirmacao == 'Sim':
            return {"PP_conhecer_projeto": confirmacao}
        else:
            # se nao tiver, recebe not_print
            return {"PP_conhecer_projeto": "NOT_PRINT", "P_pesquisaCientifica": "NOT_PRINT", "QQ_confirmacao_pesquisa": "NOT_PRINT"}

    async def validate_P_pesquisaCientifica(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação da pesquisa, aceitando texto """

        if value != '':
            return {"P_pesquisaCientifica": value}
        else:
            dispatcher.utter_message("Não entendi, vamos de novo...")
            return {"P_pesquisaCientifica": None}


    async def validate_QQ_confirmacao_pesquisa(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação da pesquisa, se tá correto ou não """

        confirmacao = tracker.get_slot("QQ_confirmacao_pesquisa")

        if confirmacao == 'Sim':
            return {"QQ_confirmacao_pesquisa": value}
        else:
            return {"P_pesquisaCientifica": None, "QQ_confirmacao_pesquisa": None}


    #  ======================= EXPERIENCIA FORM =======================
    async def validate_Q_conhecer_experiencia(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do experiencia """

        confirmacao = tracker.get_slot("Q_conhecer_experiencia")

        if confirmacao == 'Sim':
            # se tiver experiencia, segue o fluxo e não pergunta sobre curso online
            return {"Q_conhecer_experiencia": value, "R_curso_online":"nao"}
        else:
            return {"SSSS_cargo": "NOT_PRINT", "SSSSS_nomeEmpresa": "NOT_PRINT", "SS_cargo_data_entrada_saida": "NOT_PRINT", "SSS_cargo_descricao": "NOT_PRINT", "S_confirmacao_experiencia": "NOT_PRINT", "Q_conhecer_experiencia": "NOT_PRINT"}


    async def validate_R_curso_online(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando curso_online """

        confirmacao = tracker.get_slot("R_curso_online")
        if confirmacao == 'sim':
            # envia link do curso gratuito caso usuário nao tenha experiência
            dispatcher.utter_message(template="utter_curso_online_link")
            return {"R_curso_online": value}
        else: 
            dispatcher.utter_message("Ok, continuando então... ")
            return {"R_curso_online": "nao"}


    async def validate_SSSS_cargo(self,
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
            return {"SSSS_cargo": value.capitalize()}
        else: 
            dispatcher.utter_message("Não entendi seu cargo. Vamos de novo! ")
            return {"SSSS_cargo": None}


    async def validate_SSSSS_nomeEmpresa(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando nome da empresa """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        # if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
        if value != '':
            return {"SSSSS_nomeEmpresa": value.capitalize()}
        else: 
            dispatcher.utter_message("Não entendi o nome da empresa. Me fala de novo... ")
            return {"SSSSS_nomeEmpresa": None}

    
    async def validate_SS_cargo_data_entrada_saida(self,
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
            return {"SS_cargo_data_entrada_saida": value}
        else:
            dispatcher.utter_message("Não entendi...")
            return {"SS_cargo_data_entrada_saida": None}


    async def validate_SSS_cargo_descricao(
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
            return {"SSS_cargo_descricao": value.capitalize()}
        else: 
            dispatcher.utter_message("Me fala de novo, não entendi... ")
            return {"SSS_cargo_descricao": None}

    async def validate_S_confirmacao_experiencia(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação da experiência """

        confirmacao = tracker.get_slot("S_confirmacao_experiencia")
        if confirmacao == 'Sim':
            return {"S_confirmacao_experiencia": confirmacao}
        else:
            return {"SSSS_cargo": None, "SSSSS_nomeEmpresa": None, "SS_cargo_data_entrada_saida": None, "SSS_cargo_descricao": None, "S_confirmacao_experiencia": None}



    #  ======================= VOLUNTÁRIO FORM =======================
    async def validate_TTTTTT_conhecer_voluntario(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação do voluntário """

        confirmacao = tracker.get_slot("TTTTTT_conhecer_voluntario")

        if confirmacao == 'Sim':
            return {"TTTTTT_conhecer_voluntario": value}
        else:
            # se nao tiver, recebe not_print
            return {"TTTTTT_conhecer_voluntario": "NOT_PRINT", "TTTTT_nome_empresa_voluntario": "NOT_PRINT", "TTTT_cargo_voluntario": "NOT_PRINT", "TTT_cargo_descricao_voluntario": "NOT_PRINT", "TT_cargo_data_entrada_saida_voluntario": "NOT_PRINT", "T_confirmacao_experiencia_voluntario": "NOT_PRINT"}

    async def validate_TTTTT_nome_empresa_voluntario(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando nome da empresa """

        # diferente de vazio
        if value != '':
            return {"TTTTT_nome_empresa_voluntario": value.capitalize(), "TTTT_cargo_voluntario": "Voluntário"}
        else: 
            dispatcher.utter_message("Não entendi o nome da empresa. Me fala de novo... ")
            return {"TTTTT_nome_empresa_voluntario": None}


    async def validate_TTTT_cargo_voluntario(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando cargo voluntário """

        # diferente de vazio
        if value != '':
            return {"TTTT_cargo_voluntario": value.capitalize()}
        else: 
            dispatcher.utter_message("Não entendi seu cargo. Vamos de novo! ")
            return {"TTTT_cargo_voluntario": None}

    
    async def validate_TT_cargo_data_entrada_saida_voluntario(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """ Validando saída do emprego """

        if value != '':
            return {"TT_cargo_data_entrada_saida_voluntario": value}
        else:
            dispatcher.utter_message("Não entendi...")
            return {"TT_cargo_data_entrada_saida_voluntario": None}


    async def validate_TTT_cargo_descricao_voluntario(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando descrição do cargo """

        # diferente de vazio
        if value != '':
            return {"TTT_cargo_descricao_voluntario": value.capitalize()}
        else: 
            dispatcher.utter_message("Me fala de novo, não entendi... ")
            return {"TTT_cargo_descricao_voluntario": None}

    async def validate_T_confirmacao_experiencia_voluntario(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validação da experiência """

        confirmacao = tracker.get_slot("T_confirmacao_experiencia_voluntario")
        if confirmacao == 'Sim':
            return {"T_confirmacao_experiencia_voluntario": confirmacao}
        else:
            return {"TTTT_cargo_voluntario": None, "TTTTT_nome_empresa_voluntario": None, "TT_cargo_data_entrada_saida_voluntario": None, "TTT_cargo_descricao_voluntario": None, "T_confirmacao_experiencia_voluntario": None}



    #  ======================= FEEDBACK FORM ============================
    async def validate_U_feedback(
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
            return {"U_feedback": value}
        else: 
            dispatcher.utter_message("Vamos de novo... ")
            return {"U_feedback": None}


    async def validate_V_nota(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """ Validando V_nota """

        # campo não vazio, única verificação
        if value != '':
            return {"V_nota": value}
        else: 
            dispatcher.utter_message("Vamos de novo... ")
            return {"V_nota": None}






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
        name = tracker.get_slot("AA_nome")
        age = tracker.get_slot("B_idade")
        address = tracker.get_slot("CC_endereco")
        city = tracker.get_slot("CCC_cidade")
        state = tracker.get_slot("C_estado")
        cellphone = tracker.get_slot("D_telefone")
        email = tracker.get_slot("E_email")

        linkedln_link = tracker.get_slot("GG_linkedln_link")
        # if linkedln_link == None:
        #     linkedln_link = "NOT_PRINT"

        area = tracker.get_slot("HH_area")
        area_level = tracker.get_slot("H_area_nivel")
        goal = tracker.get_slot("L_objetivo")
        scholarity = tracker.get_slot("II_escolaridade")
        courseName = tracker.get_slot("JJ_cursoNome")
        courseSchool = tracker.get_slot("J_institutoNome")
        courseEndYear = tracker.get_slot("K_previsaoTermino")

        courses = tracker.get_slot("NN_habilidade")
        # if courses == None:
        #     courses = "NOT_PRINT"

        language = tracker.get_slot("OOO_idioma")
        # if language == None:
        #     language = "NOT_PRINT"
        language_level = tracker.get_slot("OO_idioma_nivel")

        cientificResearch = tracker.get_slot("P_pesquisaCientifica")
        # if cientificResearch == None:
        #     cientificResearch = "NOT_PRINT"

        companyName = tracker.get_slot("SSSSS_nomeEmpresa")
        if companyName == None:
            companyName = "Primeiro emprego objetivando adquirir conhecimento e experiência necessária junto à empresa."

        companyOccupation = tracker.get_slot("SSSS_cargo")
        # if companyOccupation == None:
        #     companyOccupation = "NOT_PRINT"

        companyDescription = tracker.get_slot("SSS_cargo_descricao")
        # if companyDescription == None:
        #     companyDescription = "NOT_PRINT"

        companyStartEnd = tracker.get_slot("SS_cargo_data_entrada_saida")
        # if companyStartEnd == None:
        #     companyStartEnd = "NOT_PRINT"


        companyNameVolunteer = tracker.get_slot("TTTTT_nome_empresa_voluntario")
        # if companyNameVolunteer == None:
        #     companyNameVolunteer = "Primeiro emprego objetivando adquirir conhecimento e experiência necessária junto à empresa."

        companyOccupationVolunteer = tracker.get_slot("TTTT_cargo_voluntario")
        # if companyOccupationVolunteer == None:
        #     companyOccupationVolunteer = "NOT_PRINT"

        companyDescriptionVolunteer = tracker.get_slot("TTT_cargo_descricao_voluntario")
        # if companyDescriptionVolunteer == None:
        #     companyDescriptionVolunteer = "NOT_PRINT"

        companyStartEndVolunteer = tracker.get_slot("TT_cargo_data_entrada_saida_voluntario")
        # if companyStartEnd == None:
        #     companyStartEnd = "NOT_PRINT"

        feedback = tracker.get_slot("U_feedback")
        grade = tracker.get_slot("V_nota")
        

        # CHAMADA DA FUNÇÃO PASSANDO OS DADOS PRA FAZER POST REQUEST
        generate_pdf(name, age, address, city, state, cellphone, email, linkedln_link, area, area_level, goal, scholarity, 
                courseName, courseSchool, courseEndYear, courses, language, language_level, cientificResearch, companyName, 
                companyOccupation, companyDescription, companyStartEnd, companyNameVolunteer, companyOccupationVolunteer,
                companyDescriptionVolunteer, companyStartEndVolunteer, feedback, grade)


        # após post request, zerando todos os slots para None
        return [
            SlotSet("AA_nome", None),
            SlotSet("A_primeiroNome", None),
            SlotSet("B_idade", None),
            SlotSet("CCCC_cep", None),
            SlotSet("CCC_cidade", None),
            SlotSet("CC_endereco", None),            
            SlotSet("C_estado", None),
            SlotSet("D_telefone", None),
            SlotSet("E_email", None),
            SlotSet("F_confirmacao_dados_basicos", None),
            SlotSet("GGG_user_has_linkedln", None),
            SlotSet("GG_linkedln_link", None),
            SlotSet("G_confirmacao_linkedln", None),
            SlotSet("HH_area", None),
            SlotSet("H_area_nivel", None),
            SlotSet("II_escolaridade", None),
            SlotSet("I_escolaridadeFormadoOuAndamento", None),
            SlotSet("JJ_cursoNome", None),
            SlotSet("J_institutoNome", None),
            SlotSet("K_previsaoTermino", None),
            SlotSet("L_objetivo", None),
            SlotSet("M_confirmacao_formacao", None),
            SlotSet("NNN_conhecer_curso", None),
            SlotSet("NN_habilidade", None),
            SlotSet("N_confirmacao_habilidade", None),
            SlotSet("OOOO_conhecer_idioma", None),
            SlotSet("OOO_idioma", None),
            SlotSet("OO_idioma_nivel", None),
            SlotSet("O_confirmacao_idioma", None),      
            SlotSet("PP_conhecer_projeto", None),
            SlotSet("P_pesquisaCientifica", None),
            SlotSet("QQ_confirmacao_pesquisa", None),
            SlotSet("Q_conhecer_experiencia", None),
            SlotSet("R_curso_online", None),
            SlotSet("SSSSS_nomeEmpresa", None),
            SlotSet("SSSS_cargo", None),
            SlotSet("SSS_cargo_descricao", None),
            SlotSet("SS_cargo_data_entrada_saida", None),
            SlotSet("S_confirmacao_experiencia", None),
            SlotSet("TTTTTT_conhecer_voluntario", None),
            SlotSet("TTTTT_nome_empresa_voluntario", None),
            SlotSet("TTTT_cargo_voluntario", None),
            SlotSet("TTT_cargo_descricao_voluntario", None),
            SlotSet("TT_cargo_data_entrada_saida_voluntario", None),
            SlotSet("T_confirmacao_experiencia_voluntario", None),
            SlotSet("U_feedback", None),
            SlotSet("V_nota", None),
        ]

        # dispatcher.utter_message("")