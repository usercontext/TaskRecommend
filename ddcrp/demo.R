counts <- c(1,0,0,0,0,0,0,2,0)
hyper = 0.5

k <- length(counts)
  idx <- counts > 0
  v <- (lgamma(k*hyper) - sum(idx)*lgamma(hyper) +
        sum(lgamma(hyper+counts[idx])) - lgamma(sum(counts[idx])+k*hyper))

print (lgamma(k*hyper))
print (k)
print (idx)
print (sum(idx))
print (counts[idx])
print (lgamma(hyper+counts[idx]))
 print (v)
 
 safelog <- function(x) {

    G.THRESH.LOG      <-  1e-200; ## threshold used to avoid numerical problem

    x[x < G.THRESH.LOG]    <- G.THRESH.LOG;

    x[x > 1./G.THRESH.LOG] <- 1./G.THRESH.LOG;

    log(x);

}













 
 window.decay <- function(w)
  function (x) (as.integer(x <= w))
  
 seq.dist <- function(i,j)
{
  if (j <= i)
    i - j
  else
    Inf
}
i=2
ndata = 10
 dist.fn=seq.dist
 decay.fn=window.decay(100)
 log.prior <- sapply(1:ndata,
                          function (j) safelog(decay.fn(dist.fn(i, j))))
print (log.prior)
                          
                          