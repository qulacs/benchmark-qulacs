
unset OMP_NUM_THREADS
unset MKL_NUM_THREADS
unset MKL_DOMAIN_NUM_THREADS
unset JULIA_NUM_THREADS

cd $1
if [ "$1" = "yao" ]; then
  julia ./benchmarks.jl
else
  pytest ./benchmarks.py --benchmark-save="data" --benchmark-sort=name --benchmark-min-rounds=5
fi
cd ../


