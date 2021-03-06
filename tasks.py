import os
import sys

from invoke import call, task

ROOT = os.path.abspath(os.path.dirname(__file__))

CLEAN_PATTERNS = [
    'build', 'dist', '**/*.pyc', '**/__pycache__', '.tox', '**/*.mo', 'reports'
]


def color(code):
    '''A simple ANSI color wrapper factory'''
    return lambda t: '\033[{0}{1}\033[0;m'.format(code, t)


green = color('1;32m')
red = color('1;31m')
cyan = color('1;36m')
white = color('1;39m')
yellow = color('1;33m')


def header(text):
    '''Display an header'''
    print(' '.join((yellow('★'), white(text), yellow('★'))))
    sys.stdout.flush()


def info(text, *args, **kwargs):
    '''Display informations'''
    text = text.format(*args, **kwargs)
    print(' '.join((cyan('➤'), text)))
    sys.stdout.flush()


def success(text):
    '''Display a success message'''
    print(' '.join((green('✔'), white(text))))
    sys.stdout.flush()


def error(text):
    '''Display an error message'''
    print(' '.join((red('✘'), yellow(text))))
    sys.stdout.flush()


def exit(text=None, code=-1):
    if text:
        error(text)
    sys.exit(-1)


@task
def clean(ctx):
    '''Cleanup all build artifacts'''
    header(clean.__doc__)
    with ctx.cd(ROOT):
        for pattern in CLEAN_PATTERNS:
            info(pattern)
            ctx.run('rm -rf {0}'.format(' '.join(CLEAN_PATTERNS)))


@task
def test(ctx, report=False, verbose=False):
    '''Run tests suite'''
    header(test.__doc__)
    cmd = ['pytest']
    if verbose:
        cmd.append('-v')
    if report:
        cmd.append('--junitxml=reports/tests.xml')
    with ctx.cd(ROOT):
        ctx.run(' '.join(cmd), pty=True)


@task
def cover(ctx, report=False, verbose=False):
    '''Run tests suite with coverage'''
    header(cover.__doc__)
    cmd = [
        'pytest',
        '--cov-config coverage.rc',
        '--cov-report term',
        '--cov=umfactory',
    ]
    if verbose:
        cmd.append('-v')
    if report:
        cmd += [
            '--cov-report html:reports/coverage',
            '--cov-report xml:reports/coverage.xml',
            '--junitxml=reports/tests.xml'
        ]
    with ctx.cd(ROOT):
        ctx.run(' '.join(cmd), pty=True)


@task
def qa(ctx):
    '''Run a quality report'''
    header(qa.__doc__)
    with ctx.cd(ROOT):
        info('Python Static Analysis')
        flake8_results = ctx.run('flake8 umfactory tests', pty=True, warn=True)
        if flake8_results.failed:
            error('There is some Python lints to fix')
        else:
            success('Python code seems OK')
        info('Ensure PyPI can render README and CHANGELOG')
        readme_results = ctx.run('python setup.py check -r -s', pty=True, warn=True, hide=True)
        if readme_results.failed:
            print(readme_results.stdout)
            error('README and/or CHANGELOG is not renderable by PyPI')
        else:
            success('README and CHANGELOG are renderable by PyPI')
    if flake8_results.failed or readme_results.failed:
        exit('Quality check failed', flake8_results.return_code or readme_results.return_code)
    success('Quality check OK')


@task
def dist(ctx, buildno=None):
    '''Package for distribution'''
    header(dist.__doc__)
    cmd = ['python setup.py']
    if buildno:
        cmd.append('egg_info -b {0}'.format(buildno))
    cmd.append('bdist_wheel')
    with ctx.cd(ROOT):
        ctx.run(' '.join(cmd), pty=True)
    success('Distribution is available in dist directory')


@task(clean, qa, call(cover, report=True), dist, default=True)
def all(ctx):
    '''Run tests, reports and packaging'''
    pass
