# -*- coding: utf-8 -*-
# Copyright (c) 2020, Matgenix SRL

"""Module containing custodian validators for SISSO."""

import os

from custodian.custodian import Validator


class NormalCompletionValidator(Validator):
    """Validator of the normal completion of SISSO."""

    def __init__(
        self,
        output_file: str = "SISSO.out",
        stdout_file: str = "SISSO.log",
        stderr_file: str = "SISSO.err",
    ):
        """Constructor for NormalCompletionValidator class.

        This validator checks that the standard error file (SISSO.err by default) is
        empty, that the standard output file is not empty and that the output file
        (SISSO.out) is completed, i.e. ends with "Have a nice day !"

        Args:
            output_file: Name of the output file (default: SISSO.log).
            stdout_file: Name of the standard output file (default: SISSO.log).
            stderr_file: Name of the standard error file (default: SISSO.err).
        """
        self.output_file = output_file
        self.stdout_file = stdout_file
        self.stderr_file = stderr_file

    def check(self) -> bool:
        """Validates the normal completion of SISSO.

        Returns:
            bool: True if the standard error file is empty, the standard output file
                is not empty and the output file ends with "Have a nice day !".
        """
        if not os.path.isfile(self.output_file):
            return True

        if not os.path.isfile(self.stdout_file):
            return True

        if os.stat(self.stdout_file).st_size == 0:
            return True

        if os.path.isfile(self.stderr_file):
            if os.stat(self.stderr_file).st_size != 0:
                return True

        with open(self.output_file, "rb") as f:
            out = f.read()

        return out.rfind(b"Have a nice day !") < 0
