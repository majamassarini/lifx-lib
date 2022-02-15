%global pypi_name         lifx-lib

Name:           python-%{pypi_name}
Version:        0.9.1
Release:        1%{?dist}
Summary:        A Python 3 library able to encode/decode Lifx (lan) messages.

License:        MIT

Url:            https://github.com/majamassarini/lifx-lib
Source0:        https://github.com/majamassarini/lifx-lib/archive/%{version}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel

%global _description %{expand:
A Python 3 library able to encode/decode Lifx (lan) messages.
}

%description %_description

%package -n     python3-%{pypi_name}
Summary:        %{summary}
%py_provides    python3-%{pypi_name}

%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{pypi_name}-%{version} -p1

%generate_buildrequires
%pyproject_buildrequires -r

%build
%pyproject_wheel

%install
%pyproject_install

%check
%{python3} -m unittest

%files -n python3-%{pypi_name}
%license LICENSE
%doc README.md
%{python3_sitelib}/lifx_lib-%{version}.dist-info/
%{python3_sitelib}/lifx

%changelog
%autochangelog
