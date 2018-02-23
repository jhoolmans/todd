class KeyBindings:
    user_keys = []
    key_bindings = {}

    def __init__(self, user_keys):
        self.user_keys = user_keys
        self.fillWithDefault()
        self.fillWithUserKeys(user_keys)

    def fillWithUserKeys(self, users_keys):
        for bind in users_keys:
            key = self.userKeysToList(users_keys[bind])
            try:
                self.key_bindings[bind] = key
            except KeyError:
                print("KeyBind \"" + bind + "\" not found")

    def fillWithDefault(self):
        self.key_bindings["home"] = ["g"]
        self.key_bindings["end"] = ["G"]
        self.key_bindings["up"] = ["k", "up"]
        self.key_bindings["down"] = ["j", "down"]
        self.key_bindings["page-up"] = ["K", "page up"]
        self.key_bindings["page-down"] = ["J", "page down"]
        self.key_bindings["left"] = ["H", "left"]
        self.key_bindings["right"] = ["L", "right"]
        self.key_bindings["quit"] = ["q"]
        self.key_bindings["save"] = ["S"]
        self.key_bindings["reload"] = ["R"]
        self.key_bindings["archive"] = ["X"]
        self.key_bindings["undo-archive"] = ["U"]
        self.key_bindings["new"] = ["n"]
        self.key_bindings["toggle-done"] = ["x"]
        self.key_bindings["priority-higher"] = ["<"]
        self.key_bindings["priority-lower"] = [">"]
        self.key_bindings["save-item"] = ["enter"]
        self.key_bindings["edit"] = ["enter", "A", "e"]
        self.key_bindings["delete"] = ["D"]
        self.key_bindings["switch-context"] = ["c"]
        self.key_bindings["toggle-sort-order"] = ["s"]
        self.key_bindings["toggle-wrapping"] = ["w"]
        self.key_bindings["toggle-help"] = ["h", "?"]
        self.key_bindings["search"] = ["/"]
        self.key_bindings["search-clear"] = ["C"]
        self.key_bindings["add-due"] = ["+"]
        self.key_bindings["subtract-due"] = ["-"]
        self.key_bindings["edit-complete"] = ["tab"]
        self.key_bindings["edit-move-left"] = ["left"]
        self.key_bindings["edit-move-right"] = ["right"]
        self.key_bindings["edit-word-left"] = ["meta b", "ctrl b"]
        self.key_bindings["edit-word-right"] = ["meta f", "ctrl f"]
        self.key_bindings["edit-end"] = ["ctrl e", "end"]
        self.key_bindings["edit-home"] = ["ctrl a", "home"]
        self.key_bindings["edit-delete-word"] = ["ctrl w"]
        self.key_bindings["edit-delete-end"] = ["ctrl k"]
        self.key_bindings["edit-delete-beginning"] = ["ctrl u"]
        self.key_bindings["edit-paste"] = ["ctrl y"]

    def __getitem__(self, index):
        return ", ".join(self.key_bindings[index])

    def userKeysToList(self, userKey):
        keys = userKey.split(",")
        return [key.strip() for key in keys]

    def getKeyBinding(self, bind):
        try:
            return self.key_bindings[bind]
        except KeyError:
            return []

    def is_bound_to(self, key, bind):
        return key in self.getKeyBinding(bind)