app_name = "social_welfare"
app_title = "Social Welfare"
app_publisher = "Student Project"
app_description = "Ward-level social welfare management system"
app_email = "hahanh29911301@gmail.com"
app_license = "mit"

add_to_apps_screen = [
	{
		"name": app_name,
		"logo": "/assets/social_welfare/images/social-welfare.svg",
		"title": app_title,
		"route": "/desk/social-welfare",
		"has_permission": "social_welfare.has_app_permission",
	}
]

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "social_welfare",
# 		"logo": "/assets/social_welfare/logo.png",
# 		"title": "Social Welfare",
# 		"route": "/social_welfare",
# 		"has_permission": "social_welfare.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/social_welfare/css/social_welfare.css"
# app_include_js = "/assets/social_welfare/js/social_welfare.js"

# include js, css files in header of web template
# web_include_css = "/assets/social_welfare/css/social_welfare.css"
# web_include_js = "/assets/social_welfare/js/social_welfare.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "social_welfare/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "social_welfare/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "social_welfare.utils.jinja_methods",
# 	"filters": "social_welfare.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "social_welfare.install.before_install"
# after_install = "social_welfare.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "social_welfare.uninstall.before_uninstall"
# after_uninstall = "social_welfare.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "social_welfare.utils.before_app_install"
# after_app_install = "social_welfare.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "social_welfare.utils.before_app_uninstall"
# after_app_uninstall = "social_welfare.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "social_welfare.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "social_welfare.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["social_welfare.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"social_welfare.tasks.all"
# 	],
# 	"daily": [
# 		"social_welfare.tasks.daily"
# 	],
# 	"hourly": [
# 		"social_welfare.tasks.hourly"
# 	],
# 	"weekly": [
# 		"social_welfare.tasks.weekly"
# 	],
# 	"monthly": [
# 		"social_welfare.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "social_welfare.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "social_welfare.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "social_welfare.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "social_welfare.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["social_welfare.utils.before_request"]
# after_request = ["social_welfare.utils.after_request"]

# Job Events
# ----------
# before_job = ["social_welfare.utils.before_job"]
# after_job = ["social_welfare.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"social_welfare.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

fixtures = [
	{
		"dt": "Role",
		"filters": [
			[
				"role_name",
				"in",
				[
					"Social Welfare Officer",
					"Social Welfare Reviewer",
					"Social Welfare Manager",
				],
			]
		],
	},
	{
		"dt": "Workflow State",
		"filters": [["workflow_state_name", "in", ["Draft", "Submitted", "Reviewing", "Approved", "Rejected", "Paid"]]],
	},
	{
		"dt": "Workflow Action Master",
		"filters": [["workflow_action_name", "in", ["Submit", "Start Review", "Approve", "Reject", "Mark as Paid", "Reset to Draft"]]],
	},
	{
		"dt": "Workflow",
		"filters": [["workflow_name", "=", "Support Application Workflow"]],
		"prefix": "zz_support_application",
	}
]
