import click

from .helpers import connect_cli, xnatpy_all_options


@click.group(name="list")
def listings():
    """
    Commands to list different XNAT objects either in machine- or human-readable formats.
    """
    pass


@listings.command()
@click.option("--filter", help="Filter criteria to select projects.")
@click.option("--header/--no-header", default=True, help="Include header in the listing or not.")
@click.option("--column", multiple=True, help="Columns to include in the listing.")
@xnatpy_all_options
def projects(column, filter, header, output_format, **kwargs):
    """List projects in the target XNAT."""
    if not column:
        column = None

    if filter:
        filter = filter.split("=")
        filter = {filter[0]: filter[1]}

    with connect_cli(**kwargs) as session:
        if output_format == "csv":
            result = session.projects.tabulate_csv(columns=column, filter=filter, header=header)
            click.echo(result.strip())
        else:
            click.echo("List of accessible projects")
            click.echo("====================================================")
            for proj in session.projects.filter(filters=filter).values():
                click.echo(proj.cli_str())


@listings.command()
@click.option("--project", help="Project id to list subjects from.")
@click.option("--filter", help="Filter criteria to select subjects.")
@click.option("--header/--no-header", default=True, help="Include header in the listing or not.")
@click.option("--column", multiple=True, help="Columns to include in the listing.")
@xnatpy_all_options
def subjects(project, column, filter, header, output_format, **kwargs):
    """List subjects in the target XNAT."""
    if not column:
        column = None

    if filter:
        filter = filter.split("=")
        filter = {filter[0]: filter[1]}

    with connect_cli(**kwargs) as session:
        if project is not None:
            subjects = session.subjects.filter(project=projects)
        else:
            subjects = session.subjects

        if output_format == "csv":
            result = subjects.tabulate_csv(columns=column, filter=filter, header=header)
            click.echo(result.strip())
        else:
            for subj in subjects.filter(filters=filter).values():
                click.echo(subj.cli_str())
