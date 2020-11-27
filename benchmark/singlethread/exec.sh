
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export MKL_DOMAIN_NUM_THREADS=1
export JULIA_NUM_THREADS=1

cd $1
if [ "$1" = "yao" ]; then
  julia ./benchmarks.jl
else
  pytest ./benchmarks.py --benchmark-save="data" --benchmark-sort=name --benchmark-min-rounds=5
fi
cd ../


