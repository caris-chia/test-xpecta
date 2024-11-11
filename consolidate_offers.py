from link_extractor import concat_csv_files

concatenated_dfs = concat_csv_files('./ofertas')

concatenated_dfs.to_csv('./output/offers.csv', index=False)
