import sublime
import sublime_plugin
import subprocess

class GitLineStatusCommand(sublime_plugin.TextCommand):
    def run(self, edit):
      self.view.erase_regions("git-line-status-added")
      self.view.erase_regions("git-line-status-deleted")

      point = self.view.text_point(4, 0)
      region = self.view.line(point)

      added_regions = [
        region
      ]

      # self.view.add_regions(
      #   "git-line-status-added",
      #   added_regions,
      #   "markup.inserted",
      #   "dot",
      #   sublime.HIDDEN | sublime.PERSISTENT
      # )

      try:
        output = subprocess.check_output([
          'git',
          'diff',
          self.view.file_name()
        ])

        print(output)
      except subprocess.CalledProcessError as error:
        print('OH NO!!!!!', error.returncode)
        print(error.output)
