#include <omp.h>
typedef int size_t;
void cfun(const double *indatav, size_t size, double *outdatav)
{
    size_t i;
    for (i = 0; i < size; ++i)
        outdatav[i] = indatav[i] * 2.0;
}
void meanf(const double *indatav, size_t size, double *outdatav,int r)
{
    size_t i,j;
    double mean=0;
	# pragma omp parallel for \
	  shared ( i ) \
	  private ( j,mean )\
	  num_threads(4)
    for (i = 0; i < size; ++i){



    	mean=0;

        for(j=i;j<i+r && j<size;j++){
        	mean=mean + indatav[j];
        }
    	outdatav[i]=mean/r;
    }
}
