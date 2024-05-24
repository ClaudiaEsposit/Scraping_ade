import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import date
today = date.today()

def scraper(ufficio,ente,anno,numero,natura):
    """
    ufficio è l'id che si trova nel file uffici_finanziari (in code)
    ente è l'id da ricavare da enti.json   (esempio 001 )
    numero da file input (rg / decreto / etc )
    anno anno con 4 cifre da file input
    natura  DI  AV  /  EM  OR
    """


    session = requests.Session()
    initial_url = 'https://www1.agenziaentrate.gov.it/servizi/tassazioneattigiudiziari/registrazione.htm'
    session.get(initial_url) 

    url1 = 'https://www1.agenziaentrate.gov.it/servizi/tassazioneattigiudiziari/registrazione.htm'
    params1 = {
        'action': 'scegliufficio',
        'ufficio': ufficio,
    }
    headers = {
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    body1 = {
        'ufficio': ufficio,
    }
    response1 = session.post(url1, headers=headers, params=params1, data=body1)
    
    if response1:
        url2 = 'https://www1.agenziaentrate.gov.it/servizi/tassazioneattigiudiziari/registrazione.htm'
        params2 = {
            'action': 'scegliente',
        }
        body2 = {
            'ente': ente,
            'anno': anno,
            'numero': numero,
            'natura' : natura,
            'snumero' : ""
        }
        response2 = session.post(url2, headers=headers, params=params2, data=body2)
        if response2 :
            soup2 = BeautifulSoup(response2.text, 'html.parser')
            if 'non trovato' in response2.text:
                rep = str(numero) + ' - ' + str(anno)
                return [ufficio, natura, ente, rep, '-', '-', '-']
            else :
                tabella = soup2.find('div', class_='panel-body')
                #print("tabella " , tabella.text)
                office = tabella.find('span', string="Atto tassato dall'ufficio di: ").find_next_sibling('span').get_text(strip=True)
                #print("Ufficio:", ufficio)
                atto = tabella.find('span', string="Tipologia atto: ").find_next_sibling('span').get_text(strip=True)
                #print("Atto:", atto)
                emesso_da = tabella.find('span', string="Emesso da: ").find_next_sibling('span').get_text(strip=True)
                #print("Emesso da:", emesso_da)
                repertorio = tabella.find('span', string="n. Repertorio - anno: ").find_next_sibling('span').get_text(strip=True)
                #print("Repertorio:", repertorio)
                attore = tabella.find('span', string="Attore: ").find_next_sibling('span').get_text(strip=True)
                #print("Attore:", attore)
                convenuto = tabella.find('span', string="Convenuto: ").find_next_sibling('span').get_text(strip=True)
                #print("Convenuto:", convenuto)
                stato = tabella.find('span', string="Stato dell'atto: ").find_next_sibling('span').get_text(strip=True)
                #print("Stato:", stato)
                return [office,atto,emesso_da,repertorio,attore,convenuto,stato]
        else :
            rep = str(numero) + ' - ' + str(anno)
            return [ufficio, natura, ente, rep, '-', '-', '-']

    else:
       return 'ufficio non trovato'   
    
list_natura_monitoria = ['DI','AV']
list_natura_ppt = ['EM','OR']

def tipo_scraper(contratto,debitore, tipo, ufficio, lista_enti, anno, numero):
    results = []
    try:
        if tipo == 'monitoria':
            natura_list = list_natura_monitoria
        elif tipo == 'ppt':
            natura_list = list_natura_ppt
        else:
            raise ValueError("Invalid tipo value")

        for natura in natura_list:
            for ente in lista_enti:
                result = scraper(ufficio, ente, anno, numero, natura)
                if isinstance(result, list):
                    if len(result) == 7:
                        results.append({
                            "contratto":contratto,
                            "debitore":debitore,
                            'ufficio': result[0],
                            'atto': result[1],
                            'emesso da': result[2],
                            'repertorio': result[3],
                            'attore': result[4],
                            'convenuto': result[5],
                            'stato': result[6]
                        })
                    else:
                        results.append({
                            "contratto":contratto,
                            "debitore":debitore,
                            'ufficio': result[0],
                            'natura': result[1],
                            'ente': result[2],
                            'repertorio': result[3],
                            'attore': '-',
                            'convenuto': '-',
                            'stato': '-'
                        })
                else:
                    print(result)
    except Exception as e:
        print(f"Error occurred: {e}")
    return results

input = pd.read_excel('Input/Cleaned/input_v1.xlsx')
results =( input
    .apply(lambda row: tipo_scraper(contratto=row['NR_Contratto'],
                                    debitore=row['Debitore'],
                                    tipo= row['tipo_ricerca'],
                                    ufficio= row['code_office'],
                                    lista_enti=row['code_ente'], anno=row['year'],numero= row['nr']), axis=1)
)

df = pd.DataFrame(results.explode().tolist())
df.to_excel(f'Output/{str(today)}_output_v1.xlsx',index=False)
