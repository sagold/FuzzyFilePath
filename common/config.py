config = {

	"debug": False,
	"log": False,
	"id": "config",
	"ffp_settings_file": "FuzzyFilePath.sublime-settings",
	"escape_dollar": '\$',
	"trigger_action": ["auto_complete", "insert_path"],
	"insert_action": ["commit_completion", "insert_best_completion"],
	"trigger_statements": ["prefix", "tagName", "style"],
	"fast_query": False,

	"base_directory": False,
	"project_directory": False,
	"disable_autocompletion": False,
	"disable_keymap_actions": False,
	"auto_trigger": True,
	"trigger": [],
	"additional_scopes": [],
	"exclude_folders": ["node\\_modules", "bower\\_components/.*/bower\\_components"],

	"post_insert_move_characters": "^[\"\'\);]*"
}
