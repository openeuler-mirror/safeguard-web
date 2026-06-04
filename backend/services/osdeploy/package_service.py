"""软件包配置服务（RPM spec 生成）"""
import logging
import os
from typing import Dict

logger = logging.getLogger(__name__)


class PackageService:
    """RPM 包配置服务"""

    @staticmethod
    def generate_spec(params: Dict[str, str]) -> Dict[str, str]:
        """生成 RPM spec 文件

        Args:
            params: 包含 package_name, version, release, summary, description 等

        Returns:
            {"status": str, "path": str, "content": str}
        """
        package_name = params.get("package_name", "oskit")
        version = params.get("version", "1.0.0")
        release = params.get("release", "1%{?dist}")
        summary = params.get("summary", "A tool for operating system.")
        description = params.get("description", "Oskit is a tools platform for operating system.")
        license_name = params.get("license", "MIT")
        source = params.get("source", "%{name}-v%{version}.tar.gz")
        build_requires = params.get("build_requires", ["gcc"])
        requires = params.get("requires", ["postgresql"])
        prep_section = params.get("prep_section", "%setup -q -n oskit")
        build_section = params.get("build_section", "make clean && make build")
        install_section = params.get("install_section",
            "mkdir -p %{buildroot}/usr/bin\nmkdir -p %{buildroot}/usr/local/oskit/static\n"
            "cp -a oskit %{buildroot}/usr/bin/\nscp -r static/ %{buildroot}/usr/local/oskit/static/")
        check_section = params.get("check_section", "")
        files_section = params.get("files_section",
            "%license LICENSE\n%doc README.md\n/usr/bin/oskit\n/usr/local/oskit/static/")
        changelog = params.get("changelog", "* Fri Mar 01 2024 - 1.0.0-1\n- Initial package")

        # 处理列表类型的字段
        build_requires_str = " ".join(build_requires) if isinstance(build_requires, list) else build_requires
        requires_str = " ".join(requires) if isinstance(requires, list) else requires

        content = f"""Name:           {package_name}
Version:        {version}
Release:        {release}
Summary:        {summary}
License:        {license_name}
Source:         {source}
BuildRequires:  {build_requires_str}
Requires:       {requires_str}
%undefine _missing_build_ids_terminate_build

%description
{description}

%prep
{prep_section}

%build
{build_section}

%install
{install_section}

%check
{check_section}

%files
{files_section}

%changelog
{changelog}
"""

        output_path = params.get("output_path", "/usr/local/oskit/oskit.spec")
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                f.write(content)
            return {
                "status": "success",
                "path": output_path,
                "content": content,
                "message": f"spec 文件已生成: {output_path}",
            }
        except Exception as e:
            logger.error(f"生成 spec 文件失败: {e}")
            return {"status": "failed", "message": f"生成 spec 文件失败: {e}"}
