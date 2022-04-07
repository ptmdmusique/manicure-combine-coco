## Scripts

run `combine_coco.py` to combine all coco inputs. Make sure to change `NUM_OF_INPUTS` to the number of inputs

run `combine-aug-data.py` to combine normal data with augmented data.

run `split-train-test.py` split the combined dataset into train and test. Make sure to change `TRAIN_TEST_RAIO` to the desired ratio of train to test

## Diagram

`input\_\*/` => `combine_coco.py` => `output-no-aug/` => `combine-aug-data.py` => `output/` => `split-train-test.py` => `manicure/`
