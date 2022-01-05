import os

from pynextsim.tests.pynextsim_test_base import PynextsimTestBase

class PynextsimfTestBase(PynextsimTestBase):
    def setUp(self):
        super(PynextsimfTestBase, self).setUp()

        self.proc_config = os.path.join(self.test_data_dir,
                'config_files/nextsim_Kara_forecast.cfg')
        self.nextsim_config = os.path.join(self.outdir, 'nextsim.cfg')

        self.inp_args = [self.outdir, self.proc_config, self.nextsim_config, '20181003', '7']

        self.proc_config_no_restart = os.path.join(self.test_data_dir,
                'config_files/nextsim_Kara_forecast_no_restart.cfg')
        self.nextsim_config_no_restart = os.path.join(self.outdir, 'nextsim_no_restart.cfg')
        self.inp_args_no_restart = [
                self.outdir, self.proc_config_no_restart,
                self.nextsim_config_no_restart, '20181003', '7']

class MockOpen(object):
    def __init__(self, fname, mode):
        self.retval = 'open_%s_%s' %(fname, mode)
    def __enter__(self):
        ''' eg with open(fname, *args) as f:
            f will be self.retval '''
        return self.retval
    def __exit__(self, *args):
        ''' called at end of with section '''
        pass
