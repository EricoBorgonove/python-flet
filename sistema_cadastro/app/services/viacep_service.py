import requests

from app.utils import only_digits

def fech_address_from_viacep(cep: str) -> dict:
    cep = only_digits(cep)
    if len(cep) != 8:
        raise ValueError("CEP deve ter 8 digitos.")
    
    url = f"https://viacep.com.br/ws/{cep}/json/"
    resp = requests.get(url, timeout= 8)
    resp.raise_for_status()

    data = resp.json()
    if data.get("erro") is True:
        raise ValueError("CEP não entrado no ViaCEP.")
    
    return {
        "logradouro" :data.get ("logradouro") or "",
        "bairro" :data.get ("bairro") or "",
        "cidade" :data.get ("localidade") or "",
        "uf" :data.get ("uf") or ""
    }