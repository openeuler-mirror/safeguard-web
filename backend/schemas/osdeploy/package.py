"""软件包配置 Pydantic 模型"""
from typing import List, Optional
from pydantic import BaseModel


class SpecParams(BaseModel):
    """RPM spec 参数"""
    package_name: str = "oskit"
    version: str = "1.0.0"
    release: str = "1%{?dist}"
    summary: str = "A tool for operating system."
    description: str = "Oskit is a tools platform for operating system."
    license: str = "MIT"
    source: str = "%{name}-v%{version}.tar.gz"
    build_requires: Optional[List[str]] = None
    requires: Optional[List[str]] = None
    prep_section: str = "%setup -q -n oskit"
    build_section: str = "make clean && make build"
    install_section: Optional[str] = None
    check_section: str = ""
    files_section: Optional[str] = None
    changelog: str = "* Fri Mar 01 2024 - 1.0.0-1\n- Initial package"
    output_path: str = "/usr/local/oskit/oskit.spec"
