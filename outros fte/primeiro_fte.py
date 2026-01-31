import flet as ft

def main (page:  ft.Page):
    page.title = "Meu primeiro app com Flet"
    
    txt = ft.Text ("Olá, Flet", size=24)
    
    def clicar(e):
        txt.value = "Você clicou no botão"
        page.update()  # atualiza a tela
        
    btn = ft.ElevatedButton("Clique aqui", on_click=clicar)
    
    page.add(txt, btn)

ft.run(main)

    
    