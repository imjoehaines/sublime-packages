import os
import re
import sublime
import sublime_plugin
import subprocess

type_data = {
  'added': ('git-line-status-added', 'markup.inserted'),
  'deleted': ('git-line-status-deleted', 'markup.deleted'),
  'modified': ('git-line-status-modified', 'comment.line')
}

hunk_regex = r'^@@ \-(?:\d+),?(\d*) \+(\d+),?(\d*) @@'

class GitLineStatusCommand(sublime_plugin.EventListener):
  # called when a view is focussed
  def on_activated_async(self, view):
    self.on_post_save_async(view)

  def on_post_save_async(self, view):
    variables = view.window().extract_variables()

    if not 'folder' in variables:
      return

    directory = variables['folder']

    os.chdir(directory)

    try:
      diff = subprocess.check_output([
        'git',
        'diff',
        '-U0', # 0 lines of context as we only care about changed lines
        '--no-color',
        view.file_name()
      ]).decode()

      added = []
      deleted = []
      modified = []

      for hunk in re.finditer(hunk_regex, diff, re.MULTILINE):
        old_line_count = int(hunk.group(1) or 1)
        first_line = int(hunk.group(2))
        new_line_count = int(hunk.group(3) or 1)

        if old_line_count == 0:
          added += range(first_line, first_line + new_line_count)
        elif new_line_count == 0:
          deleted.append(first_line + 1)
        else:
          modified += range(first_line, first_line + new_line_count)

      self.add_icon_to_lines(view, 'added', added)
      self.add_icon_to_lines(view, 'deleted', deleted)
      self.add_icon_to_lines(view, 'modified', modified)
    except subprocess.CalledProcessError as error:
      print('OH NO!!!!!', error.returncode)
      print(error.output)

  def add_icon_to_lines(self, view, type, lines):
    regions = []

    for line_number in lines:
      point = view.text_point(line_number - 1, 0)
      regions.append(view.line(point))

    key, scope = type_data[type]

    view.add_regions(
      key,
      regions,
      scope,
      'dot',
      sublime.HIDDEN | sublime.PERSISTENT
    )
