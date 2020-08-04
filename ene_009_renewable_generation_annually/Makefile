.PHONY: default
default: generation capacity

.PHONY: capacity
capacity:
	python ene_XXX_renewable_capacity_annually.py

.PHONY: generation
generation:
	python ene_XXX_renewable_generation_annually.py

.PHONY: clean
clean:
	rm *.zip
	rm ene_XXX_renewable_capacity_annually_edit.csv
	rm ene_XXX_renewable_generation_annually_edit.csv
