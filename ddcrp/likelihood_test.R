mdat <- matrix(c(1,2,3, 11,12,13,1,2,3,3,4,44), nrow = 4, ncol = 3)
z <- matrix(c(2,4), nrow = 1, ncol = 2)
x=mdat[z,]
idx <- x>0
k <- length(mdat)
hyper = 0.5
print(x[idx])
v <- (lgamma(k*hyper) - sum(idx)*lgamma(hyper) +
        sum(lgamma(hyper+x[idx])) - lgamma(sum(x[idx])+k*hyper))
print(v)