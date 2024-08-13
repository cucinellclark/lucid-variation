package Bio::P3::LucidVariation::AppConfig;

use constant        lvar_service_data      => '/home/ac.cucinell/LUCID/Variation/variation_pipeline/broad_genome_data';

use base 'Exporter';
our @EXPORT_OK = qw(lvar_service_data);
our %EXPORT_TAGS = (all => [@EXPORT_OK]);
1;
