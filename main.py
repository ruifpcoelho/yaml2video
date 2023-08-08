from modules import *

# TODO: test with a different campaigns_path

if __name__ == '__main__':

    arguments = get_arguments()
    arguments_campaigns = arguments.get('campaigns', None)
    campaigns_path = get_campaigns_list(arguments_campaigns)

    print(campaigns_path)
    campaigns_config = []
    for campaign_path in campaigns_path:
        # Excecutes the full video creation process per campaign.
        # Each campaign is independent.

        # Get campaign definition
        campaign_config = get_campaign_from_path(campaign_path)
        campaigns_config.extend(campaign_config)

    for index, campaign_config in enumerate(campaigns_config):
        campaign_config['_process']['id'] = index
        # Validate settings and apply default values
        merged_campaign_config = validate_campaign_settings(campaign_config)

        # Process campaign
        result = create_video_from_campaign_config(merged_campaign_config)
