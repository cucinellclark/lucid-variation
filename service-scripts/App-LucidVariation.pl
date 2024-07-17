#
# The ComparativeSystems application
#

use Bio::KBase::AppService::AppScript;
use Bio::KBase::AppService::AppConfig;

use strict;
use Data::Dumper;
use File::Basename;
use File::Slurp;
use File::Temp;
use LWP::UserAgent;
use JSON::XS;
use IPC::Run qw(run);
use Cwd;
use Clone;
use P3DataAPI;

my $script = Bio::KBase::AppService::AppScript->new(\&process_variation, \&preflight);

my $rc = $script->run(\@ARGV);

exit $rc;

# TODO: copy RNASeq preflight
sub preflight
{

}

sub process_variation
{
    my($app, $app_def, $raw_params, $params) = @_;  
    
    print 'Proc comparative systems ', Dumper($app_def, $raw_params, $params);

    my $token = $app->token();
    my $ws = $app->workspace();

    # CLEANUP = 0 (dont delete), CLEANUP = 1 (delete)
    my $cwd = File::Temp->newdir( CLEANUP => 0 ); 

    my $work_dir = "$cwd/work";    

    -d $work_dir or mkdir $work_dir or die "Cannot mkdir $work_dir: $!";

    my $data_api = Bio::KBase::AppService::AppConfig->data_api_url;
    my $dat = { data_api => $data_api };
    my $sstring = encode_json($dat);

    my $parallel = $ENV{P3_ALLOCATED_CPU};

    #
    # Write job description.
    #  
    my $jdesc = "$cwd/jobdesc.json";
    open(JDESC, ">", $jdesc) or die "Cannot write $jdesc: $!";
    print JDESC JSON::XS->new->pretty(1)->encode($params_to_app);
    close(JDESC);

    ### TODO: make QA a separate repo

    ### TODO: change prepare_config.py or add data locations to jobdesc.json

    # Prepare config file
    # - assuming previous bvbrc setup
    # parser.add_argument('--job_json',help="Job Json file with samples, reference genome id, conditions, etc",required=True)
    # parser.add_argument('--config_file',help="Output name for the generated snakemake config file",default='job_config.json')
    my $job_config = "$cwd/job_config.json" 
    my @prep_cmd = ('prepare_config.py','--job_json',$jdesc,'--config_file',$job_config);
    warn Dumper (\@prep_cmd, $params_to_app);
    my $prep_ok = run(\@prep_cmd);

    if (!$prep_ok) 
    {
        die "prepare_config.py failed: @prep_cmd\n";
    }
    die 'testing prepare config';

    my @var_cmd = ('run_variation.py','--config',$job_config);
    my $var_ok = run(\@var_cmd);
    if (!$var_ok)
    {
        die "run_variation.py failed: @var_cmd\n";
    }
}
