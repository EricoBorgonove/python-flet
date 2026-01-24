import flet as ft 

def main (page: ft.Page):
    page.title = "Mini Cadastro - Flet"
    page.padding = 20
    
    # ESTADOS (dados do app)
    
    registros = []
    selecionado_id = None
    prox_id = 1
    
    #Controles (inputs e botões)
    
    nome = ft.TextField(label = "Nome", width=300)
    idade = ft.TextField(label="Idade",width=120, keyboard_type=ft.KeyboardType.Number)
    
    msg = ft.Text()
    
    lista = ft.Column(spacing=5)
    
    btn_salvar = ft.ElevatedButton("Salvar")
    btn_excluir = ft.OutlinedButton("Excluir Selecionado", disabled=True)
    btn_limpar = ft.TextButton("Limpar Seleção")
    
    #Funções Auxiliares
    
    def limpar_campos():
        nome.value = ""
        idade.value = ""
    
    def set_mensagem (texto, cor=ft.Colors.BLACK):
        msg.value = texto
        msg.color = cor
        
    def obter_registros_por_id(_id):
        for r in registros:
            if r["id"] == _id:
                return r
        return None
    
    #RENDERIZAÇÃO DA LISTA
    
    
    
    def renderizar_lista():
        lista.controls.clear()

        if not registros:
            lista.controls.append(ft.Text("Nenhum registro ainda."))
            return

        for r in registros:
            is_sel = (r["id"] == selecionado_id)

            item = ft.Container(
                padding=10,
                border_radius=10,
                bgcolor=ft.Colors.BLUE_50 if is_sel else None,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(f"#{r['id']} — {r['nome']} ({r['idade']})"),
                        ft.Text("Selecionado" if is_sel else ""),
                    ],
                ),
                on_click=lambda e, rid=r["id"]: selecionar(rid),
            )

            lista.controls.append(item)