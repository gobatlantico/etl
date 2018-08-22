# ETL - Sistema Interno de Gestión de Datos Abiertos
> Gobernación del Atlántico - Retos Máxima Velocidad 2018


[![NPM Version][npm-image]][npm-url]
[![Build Status][travis-image]][travis-url]
[![Downloads Stats][npm-downloads]][npm-url]


Aplicación web que facilita, agiliza, controla y organiza las publicaciones de datos abiertos de la Gobernación del Atlántico  en datos.gov.co del MinTIC. Impactando en los indicadores de Gobierno en Línea y apoyando directamente el cumplimiento de la ley de Transparencia y del Derecho de Acceso a la Información Pública 1712 de 2014 e indirectamente proyectos como “emprende con datos” del MinTIC y Findeter.

![](header.png)

## Installation

OS X & Linux:

```sh
npm install my-crazy-module --save
```
1. INSTALAR PYTHON 3.5
  1. INSTALAR PRE REQUISITOS
```sh
yum install gcc
```
2. DESCARGAR PYTHON 3.5.1
```sh
# cd /opt
# wget https://www.python.org/ftp/python/3.5.1/Python-3.5.1.tgz
```
3. EXTRAER ARCHIVO Y COMPILAR
```sh
# tar xzf Python-3.5.1.tgz
# cd Python-3.5.1
# ./configure
# make altinstall
```
4. CONFIRMAR VERSIÓN DE PYTHON
```sh
# python3.5 -V
# python3.5 --version
```
2. CREAR AMBIENTE VIRTUAL
Crear un ambiente virtual, el ambiente virtual SOLO puede contener MINÚSCULAS
```sh
python3 -m venv nombredelambiente
```
POR EJEMPLO:
```sh
python3 -m venv vetlgob
```
El comando anterior creará un ambiente virtual llamado vetlgob en la carpeta donde se ejecute el comando.
3. ACTIVAR EL ENTORNO VIRTUAL
Para activar el ambiente virtual utilice el siguiente comando:
```sh
source /ruta/del/ambiente/virtual/bin/activate
```
POR EJEMPLO:
```sh
source /vetlgob/bin/activate
```
4. INSTALAR DEPENDENCIAS CON PIP
Se instalan las dependencias necesarias con el siguiente comando:
```sh
pip install pandas xlrd django==1.11.5 cx_Oracle django.crontab
sodapy psycopg2
```
En caso de tener el problemas con “SNIMissingWarning” instalar también:
```sh
pip install ‘request[security]’
```
5. CONECTAR CON POSTGRESQL
Windows:

```sh
edit autoexec.bat
```

## Usage example

A few motivating and useful examples of how your product can be used. Spice this up with code blocks and potentially more screenshots.

_For more examples and usage, please refer to the [Wiki][wiki]._

## Development setup

Describe how to install all development dependencies and how to run an automated test-suite of some kind. Potentially do this for multiple platforms.

```sh
make install
npm test
```

## Release History

* 0.2.1
    * CHANGE: Update docs (module code remains unchanged)
* 0.2.0
    * CHANGE: Remove `setDefaultXYZ()`
    * ADD: Add `init()`
* 0.1.1
    * FIX: Crash when calling `baz()` (Thanks @GenerousContributorName!)
* 0.1.0
    * The first proper release
    * CHANGE: Rename `foo()` to `bar()`
* 0.0.1
    * Work in progress

## Meta

Your Name – [@YourTwitter](https://twitter.com/dbader_org) – YourEmail@example.com

Distributed under the XYZ license. See ``LICENSE`` for more information.

[https://github.com/yourname/github-link](https://github.com/dbader/)

## Contributing

1. Fork it (<https://github.com/yourname/yourproject/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

<!-- Markdown link & img dfn's -->
[npm-image]: https://img.shields.io/npm/v/datadog-metrics.svg?style=flat-square
[npm-url]: https://npmjs.org/package/datadog-metrics
[npm-downloads]: https://img.shields.io/npm/dm/datadog-metrics.svg?style=flat-square
[travis-image]: https://img.shields.io/travis/dbader/node-datadog-metrics/master.svg?style=flat-square
[travis-url]: https://travis-ci.org/dbader/node-datadog-metrics
[wiki]: https://github.com/yourname/yourproject/wiki
