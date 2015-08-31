%global ext_name uploadprogress
%global ini_name 20-%{ext_name}.ini
%global php php55u
%global with_zts 0%{?__ztsphp:1}

Name: %{php}-pecl-%{ext_name}
Version: 1.0.3.1
Release: 1.ius%{?dist}
Summary: An extension to track progress of a file upload
Group: Development/Libraries
License: PHP
URL: https://pecl.php.net/package/%{ext_name}
Source0: https://pecl.php.net/get/%{ext_name}-%{version}.tgz

BuildRequires: %{php}-devel
Requires: %{php}(api) = %{php_core_api}
Requires: %{php}(zend-abi) = %{php_zend_api}
Requires(post): %{php}-pear
Requires(postun): %{php}-pear

Provides: php-pecl-%{ext_name} = %{version}-%{release}
Provides: php-pecl-%{ext_name}%{?_isa} = %{version}-%{release}
Provides: %{php}-%{ext_name} = %{version}-%{release}
Provides: %{php}-%{ext_name}%{?_isa} = %{version}-%{release}
Provides: php-%{ext_name} = %{version}-%{release}
Provides: php-%{ext_name}%{?_isa} = %{version}-%{release}
Provides: %{php}-pecl(%{ext_name}) = %{version}
Provides: %{php}-pecl(%{ext_name})%{?_isa} = %{version}
Provides: php-pecl(%{ext_name}) = %{version}
Provides: php-pecl(%{ext_name})%{?_isa} = %{version}

Conflicts: php-%{ext_name} < %{version}
Conflicts: php-pecl-%{ext_name} < %{version}

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter private shared object
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
An extension to track progress of a file upload.


%prep
%setup -q -c

mv %{ext_name}-%{version} nts
%if %{with_zts}
cp -pr nts zts
%endif

cat > %{ini_name} << EOF
; Enable %{ext_name} extension module
extension=%{ext_name}.so
EOF


%build
pushd nts
%{_bindir}/phpize
%configure --with-php-config=%{_bindir}/php-config
%{__make} %{?_smp_mflags}
popd

%if %{with_zts}
pushd zts
%{_bindir}/zts-phpize
%configure --with-php-config=%{_bindir}/zts-php-config
%{__make} %{?_smp_mflags}
popd
%endif


%install
%{__make} -C nts install INSTALL_ROOT=%{buildroot}
%{__install} -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

%if %{with_zts}
%{__make} -C zts install INSTALL_ROOT=%{buildroot}
%{__install} -D -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

%{__install} -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml


%check
pushd nts
# simple module load test
%{__php} --no-php-ini \
    --define extension_dir=%{buildroot}%{php_extdir}/\
    --define extension=%{ext_name}.so \
    --modules | grep uploadprogress
popd

%if %{with_zts}
pushd zts
%{__ztsphp} --no-php-ini \
    --define extension_dir=%{buildroot}%{php_ztsextdir}/\
    --define extension=%{ext_name}.so \
    --modules | grep uploadprogress
popd
%endif


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%doc nts/examples
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{ext_name}.so

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{ext_name}.so
%endif


%changelog
* Mon Aug 31 2015 Carl George <carl.george@rackspace.com> - 1.0.3.1-1.ius
- Initial spec file
