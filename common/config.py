config = {

	"DEBUG": False,
	"LOG": False,
	"FFP_SETTINGS_FILE": "FuzzyFilePath.sublime-settings",
	"ESCAPE_DOLLAR": '\$',
	"TRIGGER_ACTION": ["auto_complete", "insert_path"],
	"INSERT_ACTION": ["commit_completion", "insert_best_completion"],
	"TRIGGER_STATEMENTS": ["prefix", "tagName", "style"],

	"BASE_DIRECTORY": False,
	"PROJECT_DIRECTORY": False,
	"DISABLE_AUTOCOMPLETION": False,
	"DISABLE_KEYMAP_ACTIONS": False,
	"AUTO_TRIGGER": True,
	"TRIGGER": [],
	"EXCLUDE_FOLDERS": ["node\\_modules", "bower\\_components/.*/bower\\_components"],

	"POST_INSERT_MOVE_CHARACTERS": "^[\"\'\);]*"
}
