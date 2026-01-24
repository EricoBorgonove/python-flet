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
            
            #Eventos - Ações dos usuários
            
    def selecionar (rid: int):
        nonlocal selecionado_id
        selecionado_id = rid
        
        r = obter_registros_por_id(rid)
        if r:
            nome.value = r["nome"]
            idade.value = r["idade"]
            
        btn_excluir.disabled = False
        set_mensagem(f"Registro #{rid} selecionado", ft.Colors.BLUE)
        renderizar_lista()
        page.update()
        
    def salvar (e):
        nonlocal prox_id, selecionado_id
        
        n = (nome.value or "").strip()
        i = (idade.value or "").strip()
        
        if not n or not i:
            set_mensagem ("Preencha Nome e Idade", ft.Colors.RED)
            page.update()
            return
        
        if selecionado_id is not None:
            r = obter_registros_por_id(selecionado_id)
            if r:
                r["nome"] = n
                r["idade"] = i
                set_mensagem(f"Registro #{selecionado_id} atualizado", ft.Colors.GREEN)
            else:
                registros.append({"id": prox_id, "nome": n, "idade":i})
                set_mensagem(f"Registro #{prox_id} criado", ft.Colors.GREEN)
                prox_id += 1
        
        limpar_campos()
        selecionado_id = None
        btn_excluir.disabled = True
        
        renderizar_lista()
        page.update()
        
    def excluir(e):
        nonlocal selecionado_id
        if selecionado_id is None:
            return
        
        r = obter_registros_por_id(selecionado_id)
        if r:
            registros.remove(r)
            set_mensagem(f"Registro #{selecionado_id} excluido", ft.Colors.ORANGE)
        
        selecionado_id = None
        btn_excluir.disabled = True
        limpar_campos()
        
        renderizar_lista()
        page.update()
        
    def limpar_selecao(e):
        nonlocal selecionado_id
        selecionado_id = None
        btn_excluir.disabled = True
        limpar_campos()
        set_mensagem("Seleção Limpa", ft.Colors.BLACK)
        
        renderizar_lista()
        page.update()
        
    # amarrar eventos nos botões
    btn_salvar.on_click = salvar
    btn_excluir.on_click = excluir
    btn_limpar.on_click = limpar_selecao
    
    #LAYOUT (organização visual)
    
    page.add(
        ft.Text("Mini Cadastro (Clique em um item para editar)", size=18, 
                                                      weight=ft.FontWeight.BOLD),
        ft.Row([nome, idade], spacing=10),
        ft.Row([btn_salvar, btn_excluir, btn_limpar], spacing=10),
        msg,
        ft.Divider(),
        ft.Text("Registros:", weight=ft.FontWeight.BOLD),
        lista,
    )
    #renderização inicial
    renderizar_lista()
    page.update()
    
ft.run(main)