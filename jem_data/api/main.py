if __name__ == '__main__':
    from jem_data.api import app_factory
    import jem_data.services.system_control as system_control
    app = app_factory(system_control.SystemControlService())
    app.run()
