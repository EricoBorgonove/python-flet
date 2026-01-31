import flet as ft
from datetime import datetime

from app.services.viacep_service import fetch_address_from_viacep
from app.repositories.excel_repo import ExcelRepo
from app.utils.strings import only_digits


def build_ui(page: ft.Page):
    page.title = "Cadastro de Usuários (Flet + ViaCEP + Excel)"
    page.window_width = 1100
    page.window_height = 780
    page.scroll = ft.ScrollMode.AUTO

    repo = ExcelRepo(file_path="cadastros.xlsx", sheet_name="usuarios")

    status = ft.Text("", selectable=True)

    # ===== Estado de seleção =====
    selected_excel_row = None  # linha real no Excel (int)
    selected_table_index = None  # índice na tabela (int)

    # Campos
    nome = ft.TextField(label="Nome *", expand=True)
    email = ft.TextField(label="E-mail *", expand=True, keyboard_type=ft.KeyboardType.EMAIL)
    telefone = ft.TextField(label="Telefone", expand=True)

    cep = ft.TextField(
        label="CEP * (somente números)",
        expand=True,
        keyboard_type=ft.KeyboardType.NUMBER,
        hint_text="Ex.: 69000-000",
    )
    logradouro = ft.TextField(label="Logradouro", expand=True)
    bairro = ft.TextField(label="Bairro", expand=True)
    cidade = ft.TextField(label="Cidade", expand=True)
    uf = ft.TextField(label="UF", width=90, max_length=2)
    numero = ft.TextField(label="Número *", width=140, keyboard_type=ft.KeyboardType.NUMBER)
    complemento = ft.TextField(label="Complemento", expand=True)

    cep_progress = ft.ProgressRing(width=18, height=18, visible=False)

    # Botões
    save_btn = ft.ElevatedButton("Salvar novo", icon=ft.Icons.SAVE)
    update_btn = ft.ElevatedButton("Salvar alterações", icon=ft.Icons.EDIT, disabled=True)
    delete_btn = ft.OutlinedButton("Excluir selecionado", icon=ft.Icons.DELETE, disabled=True)
    refresh_btn = ft.OutlinedButton("Atualizar tabela", icon=ft.Icons.REFRESH)

    # ===== TABELA =====
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Data/Hora")),
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("E-mail")),
            ft.DataColumn(ft.Text("Telefone")),
            ft.DataColumn(ft.Text("CEP")),
            ft.DataColumn(ft.Text("Logradouro")),
            ft.DataColumn(ft.Text("Bairro")),
            ft.DataColumn(ft.Text("Cidade")),
            ft.DataColumn(ft.Text("UF")),
            ft.DataColumn(ft.Text("Número")),
            ft.DataColumn(ft.Text("Complemento")),
        ],
        rows=[],
        heading_row_height=42,
        data_row_min_height=40,
        data_row_max_height=56,
    )

    def set_status(msg: str, error: bool = False):
        status.value = msg
        status.color = ft.Colors.RED if error else ft.Colors.GREEN
        page.update()

    def clear_status():
        status.value = ""
        page.update()

    def clear_form():
        nome.value = ""
        email.value = ""
        telefone.value = ""
        cep.value = ""
        logradouro.value = ""
        bairro.value = ""
        cidade.value = ""
        uf.value = ""
        numero.value = ""
        complemento.value = ""

    def validate_required() -> tuple[bool, str]:
        if not nome.value.strip():
            return False, "Nome é obrigatório."
        if not email.value.strip():
            return False, "E-mail é obrigatório."
        if len(only_digits(cep.value)) != 8:
            return False, "CEP inválido. Informe 8 dígitos."
        if not numero.value.strip():
            return False, "Número é obrigatório."
        return True, ""

    def fill_address(addr: dict):
        logradouro.value = addr.get("logradouro", "")
        bairro.value = addr.get("bairro", "")
        cidade.value = addr.get("cidade", "")
        uf.value = addr.get("uf", "")
        page.update()

    def set_selected(excel_row: int | None, table_index: int | None):
        nonlocal selected_excel_row, selected_table_index
        selected_excel_row = excel_row
        selected_table_index = table_index

        has_sel = selected_excel_row is not None
        update_btn.disabled = not has_sel
        delete_btn.disabled = not has_sel
        page.update()

    def load_user_to_form(user: dict):
        nome.value = str(user.get("nome", "") or "")
        email.value = str(user.get("email", "") or "")
        telefone.value = str(user.get("telefone", "") or "")
        cep.value = str(user.get("cep", "") or "")
        logradouro.value = str(user.get("logradouro", "") or "")
        bairro.value = str(user.get("bairro", "") or "")
        cidade.value = str(user.get("cidade", "") or "")
        uf.value = str(user.get("uf", "") or "")
        numero.value = str(user.get("numero", "") or "")
        complemento.value = str(user.get("complemento", "") or "")
        page.update()

    def on_cep_change(e: ft.ControlEvent):
        clear_status()
        c = only_digits(cep.value)
        if len(c) == 8:
            cep_progress.visible = True
            page.update()
            try:
                addr = fetch_address_from_viacep(c)
                fill_address(addr)
                set_status("Endereço preenchido via ViaCEP.")
            except Exception as ex:
                set_status(f"Falha ao consultar CEP: {ex}", error=True)
            finally:
                cep_progress.visible = False
                page.update()

    cep.on_change = on_cep_change

    def refresh_table():
        users = repo.list_users()  # inclui _excel_row (linha real no Excel)
        rows = []

        def make_on_select(user: dict, idx: int):
            def handler(e: ft.ControlEvent):
                set_selected(user["_excel_row"], idx)
                load_user_to_form(user)
                set_status("Registro carregado para edição.")
                # destaca visualmente a linha selecionada
                for i, r in enumerate(table.rows):
                    r.selected = (i == idx)
                page.update()

            return handler

        for idx, u in enumerate(users):
            rows.append(
                ft.DataRow(
                    selected=(idx == selected_table_index),
                    on_select_change=make_on_select(u, idx),
                    cells=[
                        ft.DataCell(ft.Text(str(u.get("data_hora", "") or ""))),
                        ft.DataCell(ft.Text(str(u.get("nome", "") or ""))),
                        ft.DataCell(ft.Text(str(u.get("email", "") or ""))),
                        ft.DataCell(ft.Text(str(u.get("telefone", "") or ""))),
                        ft.DataCell(ft.Text(str(u.get("cep", "") or ""))),
                        ft.DataCell(ft.Text(str(u.get("logradouro", "") or ""))),
                        ft.DataCell(ft.Text(str(u.get("bairro", "") or ""))),
                        ft.DataCell(ft.Text(str(u.get("cidade", "") or ""))),
                        ft.DataCell(ft.Text(str(u.get("uf", "") or ""))),
                        ft.DataCell(ft.Text(str(u.get("numero", "") or ""))),
                        ft.DataCell(ft.Text(str(u.get("complemento", "") or ""))),
                    ],
                )
            )

        table.rows = rows
        page.update()

    def on_save_new(e: ft.ControlEvent):
        ok, msg = validate_required()
        if not ok:
            set_status(msg, error=True)
            return

        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            nome.value.strip(),
            email.value.strip(),
            telefone.value.strip(),
            only_digits(cep.value),
            logradouro.value.strip(),
            bairro.value.strip(),
            cidade.value.strip(),
            uf.value.strip().upper(),
            numero.value.strip(),
            complemento.value.strip(),
        ]

        try:
            repo.append_user(row)
            set_status("Novo cadastro salvo.")
            clear_form()
            set_selected(None, None)
            refresh_table()
        except Exception as ex:
            set_status(f"Erro ao salvar: {ex}", error=True)

    def on_update_selected(e: ft.ControlEvent):
        nonlocal selected_excel_row
        if selected_excel_row is None:
            set_status("Selecione um registro na tabela para editar.", error=True)
            return

        ok, msg = validate_required()
        if not ok:
            set_status(msg, error=True)
            return

        # Atualiza data/hora para "agora" (simples e claro)
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            nome.value.strip(),
            email.value.strip(),
            telefone.value.strip(),
            only_digits(cep.value),
            logradouro.value.strip(),
            bairro.value.strip(),
            cidade.value.strip(),
            uf.value.strip().upper(),
            numero.value.strip(),
            complemento.value.strip(),
        ]

        try:
            repo.update_user(selected_excel_row, row)
            set_status("Alterações salvas.")
            clear_form()
            set_selected(None, None)
            refresh_table()
        except Exception as ex:
            set_status(f"Erro ao atualizar: {ex}", error=True)

    def on_delete_selected(e: ft.ControlEvent):
        nonlocal selected_excel_row
        if selected_excel_row is None:
            set_status("Selecione um registro na tabela para excluir.", error=True)
            return

        def confirm_delete(_):
            nonlocal selected_excel_row
            try:
                repo.delete_user(selected_excel_row)
                set_status("Registro excluído.")
                clear_form()
                set_selected(None, None)
                dlg.open = False
                page.update()
                refresh_table()
            except Exception as ex:
                dlg.open = False
                page.update()
                set_status(f"Erro ao excluir: {ex}", error=True)

        def cancel_delete(_):
            dlg.open = False
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar exclusão"),
            content=ft.Text("Tem certeza que deseja excluir o registro selecionado?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel_delete),
                ft.ElevatedButton("Excluir", icon=ft.Icons.DELETE, on_click=confirm_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def on_refresh_click(e: ft.ControlEvent):
        refresh_table()
        set_status("Tabela atualizada.")

    save_btn.on_click = on_save_new
    update_btn.on_click = on_update_selected
    delete_btn.on_click = on_delete_selected
    refresh_btn.on_click = on_refresh_click

    # Primeira carga
    refresh_table()

    page.add(
        ft.Column(
            controls=[
                ft.Text("Cadastro de Usuários", size=22, weight=ft.FontWeight.BOLD),
                ft.Text("Clique em uma linha da tabela para carregar nos campos e editar/excluir."),
                ft.Divider(),
                ft.Row([nome, email], spacing=12),
                ft.Row([telefone], spacing=12),
                ft.Row(
                    [
                        ft.Container(content=ft.Row([cep, cep_progress], spacing=8), expand=True),
                        uf,
                        numero,
                    ],
                    spacing=12,
                ),
                ft.Row([logradouro], spacing=12),
                ft.Row([bairro, cidade], spacing=12),
                ft.Row([complemento], spacing=12),
                ft.Row([save_btn, update_btn, delete_btn, refresh_btn], spacing=12),
                ft.Divider(),
                status,
                ft.Divider(),
                ft.Text("Cadastros salvos", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column([table], scroll=ft.ScrollMode.AUTO),
                    border=ft.border.all(1, ft.Colors.OUTLINE),
                    padding=8,
                    border_radius=10,
                ),
            ],
            spacing=10,
        )
    )
