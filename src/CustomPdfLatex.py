import os
import shutil
import subprocess
import tempfile

from pdflatex import PDFLaTeX


class CustomPdfLatex(PDFLaTeX):

    def __init__(self, latex_src, job_name: str):
        super().__init__(latex_src, job_name)

    @classmethod
    def from_texfile(cls, filename):
        prefix = os.path.basename(filename)
        prefix = os.path.splitext(prefix)[0]
        with open(filename, 'r', encoding="utf-8") as f:

            print(f.read().encode("utf-8"))
            return cls(f.read().encode("utf-8"), prefix)

    def create_pdf(self, keep_pdf_file: bool = False, keep_log_file: bool = False, env: dict = None):
        if self.interaction_mode is not None:
            self.add_args({'-interaction-mode': self.interaction_mode})

        dir = self.params.get('-output-directory')
        filename = self.params.get('-jobname')

        if filename is None:
            filename = self.job_name
        if dir is None:
            dir = ""

        with tempfile.TemporaryDirectory() as td:
            self.set_output_directory(td)
            self.set_jobname('file')

            args = self.get_run_args()
            fp = subprocess.run(args, input=self.latex, env=env, timeout=15, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            #with open(os.path.join(td, 'file.pdf'), 'rb') as f:
            #    self.pdf = f.read()
            with open(os.path.join(td, 'file.log'), 'rb') as f:
                self.log = f.read()
            if keep_log_file:
                shutil.move(os.path.join(td, 'file.log'), os.path.join(dir, filename + '.log'))
            if keep_pdf_file:
                shutil.move(os.path.join(td, 'file.pdf'), os.path.join(dir, filename + '.pdf'))

        return self.pdf, self.log, fp
