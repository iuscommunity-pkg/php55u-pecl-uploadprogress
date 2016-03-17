%global pecl_name uploadprogress
%global ini_name 20-%{pecl_name}.ini
%global php php55u
%global with_zts 0%{?__ztsphp:1}

Name: %{php}-pecl-%{pecl_name}
Version: 1.0.3.1
Release: 2.ius%{?dist}
Summary: An extension to track progress of a file upload
Group: Development/Libraries
License: PHP
URL: https://pecl.php.net/package/%{pecl_name}
Source0: https://pecl.php.net/get/%{pecl_name}-%{version}.tgz

BuildRequires: %{php}-pear
BuildRequires: %{php}-devel
Requires: %{php}(api) = %{php_core_api}
Requires: %{php}(zend-abi) = %{php_zend_api}
Requires(post): %{php}-pear
Requires(postun): %{php}-pear

# provide the stock name
Provides: php-pecl-%{pecl_name} = %{version}
Provides: php-pecl-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names without pecl
Provides: php-%{pecl_name} = %{version}
Provides: php-%{pecl_name}%{?_isa} = %{version}
Provides: %{php}-%{pecl_name} = %{version}
Provides: %{php}-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names in pecl() format
Provides: php-pecl(%{pecl_name}) = %{version}
Provides: php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides: %{php}-pecl(%{pecl_name}) = %{version}
Provides: %{php}-pecl(%{pecl_name})%{?_isa} = %{version}

# conflict with the stock name
Conflicts: php-%{pecl_name} < %{version}
Conflicts: php-pecl-%{pecl_name} < %{version}

# RPM 4.8
%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_setup}
# RPM 4.9
%global __provides_exclude_from %{?__provides_exclude_from:%__provides_exclude_from|}%{php_extdir}/.*\\.so$


%description
An extension to track progress of a file upload.


%prep
%setup -q -c

mv %{pecl_name}-%{version} nts
%if %{with_zts}
cp -pr nts zts
%endif

cat > %{ini_name} << EOF
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
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

%{__install} -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml


%check
# simple module load test
%{__php} --no-php-ini \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

%if %{with_zts}
%{__ztsphp} --no-php-ini \
    --define extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}
%endif


%post
%{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%doc nts/examples
%{pecl_xmldir}/%{pecl_name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Thu Mar 17 2016 Carl George <carl.george@rackspace.com> - 1.0.3.1-2.ius
- Clean up provides
- Clean up filters
- Install package.xml as %%{pecl_name}.xml, not %%{name}.xml
- Explicitly build require pear
- Clean up %%check

* Mon Aug 31 2015 Carl George <carl.george@rackspace.com> - 1.0.3.1-1.ius
- Initial spec file
