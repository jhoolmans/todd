import urwid
import collections

class MenuButton(urwid.Button):
    def __init__(self, todo, colorscheme, editing=False, wrapping='clip', border='no border'):
        super(MenuButton, self).__init__("")
        self.todo        = todo
        self.wrapping    = wrapping
        self.border      = border
        self.colorscheme = colorscheme
        self.editing     = editing
        # urwid.connect_signal(self, 'click', callback)
        if editing:
            self.edit_item()
        else:
            self.update_todo()

    def selectable(self):
        return True

    def update_todo(self):
        text = urwid.Text(self.todo.colored, wrap=self.wrapping)
        if self.border == 'bordered':
            text = urwid.LineBox(text)
        self._w = urwid.AttrMap( urwid.AttrMap(
            text,
            None, 'selected'),
            None, self.colorscheme.focus_map)

    def edit_item(self):
        self.editing = True
        self._w = urwid.Edit(caption="", edit_text=self.todo.raw)

    def save_item(self):
        self.todo.update(self._w.edit_text.strip())
        self.update_todo()
        self.editing = False

    def keypress(self, size, key):
        if self.editing:
            if key in ['down', 'up']:
                return None # don't pass up or down to the ListBox
            elif key is 'enter':
                self.save_item()
                return key
            else:
                return self._w.keypress(size, key)
        else:
            if key in ['enter', 'e', 'A']:
                self.edit_item()
                return key
            else:
                return key

class UrwidUI:
    def __init__(self, todos, colorscheme):
        self.wrapping    = collections.deque(['clip', 'space'])
        self.border      = collections.deque(['no border', 'bordered'])

        self.todos       = todos

        self.colorscheme = colorscheme
        self.palette     = [ (key, '', '', '', value['fg'], value['bg']) for key, value in self.colorscheme.colors.items() ]

    def move_selection_down(self):
        self.listbox.keypress((0, self.loop.screen_size[1]-2), 'down')

    def move_selection_up(self):
        self.listbox.keypress((0, self.loop.screen_size[1]-2), 'up')

    def keystroke(self, input):
        focus_index = self.listbox.get_focus()[1]

        if input in ('q', 'Q'):
            raise urwid.ExitMainLoop()

        # Movement
        elif input is 'g':
            self.listbox.set_focus(0)
        elif input is 'G':
            self.listbox.set_focus(len(self.listbox.body)-1)
        elif input is 'k':
            self.move_selection_up()
        elif input is 'j':
            self.move_selection_down()
        elif input is 'J':
            if focus_index+1 < len(self.listbox.body):
                self.todos.swap(focus_index, focus_index + 1)
                self.listbox.body[focus_index].todo = self.todos[focus_index]
                self.listbox.body[focus_index+1].todo = self.todos[focus_index+1]
                self.listbox.body[focus_index].update_todo()
                self.listbox.body[focus_index+1].update_todo()
                self.move_selection_down()
        elif input is 'K':
            if focus_index > 0:
                self.todos.swap(focus_index, focus_index - 1)
                self.listbox.body[focus_index].todo = self.todos[focus_index]
                self.listbox.body[focus_index-1].todo = self.todos[focus_index-1]
                self.listbox.body[focus_index].update_todo()
                self.listbox.body[focus_index-1].update_todo()
                self.move_selection_up()

        # View options
        elif input is 'c':
            self.view.widget_list.append(urwid.SolidFill('#'))
        elif input is 'w':
            self.wrapping.rotate(1)
            for widget in self.listbox.body:
                widget.wrapping = self.wrapping[0]
                widget.update_todo()
        elif input is 'l':
            self.border.rotate(1)
            for widget in self.listbox.body:
                widget.border = self.border[0]
                widget.update_todo()

        # Editing
        elif input is 'x':
            focus = self.listbox.get_focus()[0]
            i = focus.todo.raw_index

            # if self.sorting > 0:
            #     i = self.selected_item

            if self.todos[i].is_complete():
                self.todos[i].incomplete()
            else:
                self.todos[i].complete()
            focus.update_todo()
        elif input is 'n':
            self.edit_item(new='append')
        elif input is 'O':
            self.edit_item(new='insert_before')
        elif input is 'o':
            self.edit_item(new='insert_after')

    def edit_item(self, new=False):
        focus_index = self.listbox.get_focus()[1]

        if new is 'append':
            new_index = self.todos.append('')
            self.listbox.body.append(MenuButton(self.todos[new_index], self.colorscheme, editing=True, wrapping=self.wrapping[0], border=self.border[0]))
        else:
            if new is 'insert_after':
                new_index = self.todos.insert(focus_index+1, '')
            elif new is 'insert_before':
                new_index = self.todos.insert(focus_index, '')

            self.listbox.body.insert(new_index, MenuButton(self.todos[new_index], self.colorscheme, editing=True, wrapping=self.wrapping[0], border=self.border[0]))

        if new:
            self.listbox.set_focus(new_index)
            edit_widget = self.listbox.body[new_index]._w
            edit_widget.edit_text += ' '
            edit_widget.set_edit_pos(len(self.todos[new_index].raw) + 1)

    def rebuild_todo_list(self):
        for t in self.todos.todo_items:
            self.items.append(MenuButton(t, self.colorscheme))

    def main(self):

        self.header = urwid.AttrMap(
            urwid.Columns( [
                urwid.Text( ('header_todo_count', " {0} Todos ".format(len(self.todos.todo_items))) ),
                # urwid.Text( " todotxt-machine ", align='center' ),
                urwid.Text( ('header_file', " {0} ".format(self.todos.file_path)), align='right' )
            ]), 'header')
        self.footer = urwid.AttrMap(
            urwid.Columns( [
            ]), 'footer')

        self.listbox = urwid.ListBox(urwid.SimpleListWalker(
            [MenuButton(t, self.colorscheme) for t in self.todos.todo_items]
        ))
        self.view    = urwid.Columns([urwid.Frame(urwid.AttrMap(self.listbox, 'plain'), header=self.header, footer=self.footer)])

        self.loop = urwid.MainLoop(self.view, self.palette, unhandled_input=self.keystroke)
        self.loop.screen.set_terminal_properties(colors=256)
        self.loop.run()
