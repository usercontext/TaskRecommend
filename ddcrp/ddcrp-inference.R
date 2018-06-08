source("decay.R")
source("helper.R")
require(stats)

library(plyr)




# ddcrp sampler

ddcrp.gibbs <- function(dat, alpha, dist.fn, decay.fn, lhood.fn,
                        niter, summary.fn = ncomp.summary,
                        log.prior.thresh=-10,
                        clust.traj=FALSE, cust.traj=FALSE)
{

  ### set up summary statistics and trajectories

  ndata <- dim(dat)[1]
  msg.inc <- 10^(floor(log10(dim(dat)[1]))-1)
  if (clust.traj)
    clust.traj <- matrix(NA, nrow=niter, ncol=ndata)
  if (cust.traj)
    cust.traj <- matrix(NA, nrow=niter, ncol=ndata)
  score <- numeric(niter)
  map.score <- 0

  ### set up initial state, summaries, and cluster likelihoods

  msg("setting up the initial state")
  st <- data.frame(idx=1:ndata, cluster=1:ndata, customer=1:ndata)
  lhood <- daply(st, .(cluster), function (df) lhood.fn(dat[df$idx,]))
  print (lhood)
  summary <- summary.fn(dat, 0, st, lhood, alpha)

  ### run for niter iterations

  for (iter in 1:niter)
  {
    msg(sprintf("iter=%d", iter))

    iter.score <- 0
    for (i in seq(2,ndata)) # note: index i = 1 is correct at the outset
    {
      if ((i %% msg.inc) == 0) msg(sprintf("%04d", i))

      ### "remove" the i-th data point from the state
      ### to do this, set its cluster to i, and set its connected data to i

      old.cluster <- st$cluster[i]
      old.customer <- st$customer[i]
      conn.i <- connections(i, st$customer)#this is for variables linking INTO i, the rest are found & updated below inside if
      print("printing connections")
      
      msg(sprintf(" %d %d", i, old.cluster))
      
      print (conn.i)
      st$cluster[conn.i] <- i
      st$customer[i] <- i

      ### if this removal splits a table update the likelihoods.
      ### note: splits only happen if c_i^{old} != i

      if (old.customer != i)
      {
        print("if satisfied")
        ### !!! do we need to use "idx"
        old.idx <- st[which(st$cluster==old.cluster),"idx"]
        print ("printing old.idx")
        print (old.idx)
        print("old likilihoods")
        print(lhood[char(old.cluster)])
        lhood[char(old.cluster)] <- lhood.fn(dat[old.idx,])#here we define the likelihood of this cluser, old.idx has all the members
        #and likl fn gives the likelihood of just these members now which is then updated to the lhood variable - which contains the lhood for all clusters
        print ("size of dat old.idx")
        print (length(dat[old.idx,]))
        print("new likilihoods")
        print(lhood[char(old.cluster)])
      }
      else
      {
        print("else satisfied")
        lhood[char(old.cluster)] <- 0
      }

      ### compute the log prior
      ### (this should be precomputed---see opt.ddcrp.gibbs below)
      #print("before prior")
      # now this is considering all possibilities of new links - the replacement links for the i-th variable
      #print("printing distances")
      #dist.values <- sapply(1:ndata, function (j) dist.fn(i, j))
      #print (dist.values)
      log.prior <- sapply(1:ndata,
                          function (j) safelog(decay.fn(dist.fn(i, j))))
                          #function (j) decay.fn(dist.fn(i, j)))
                          #function (j) safelog(dist.fn(i, j)+1))
      
      #print ("printing log prior")
      #print (i)
      
      #print(length(dist.values))
      #print(length(log.prior))
      #print("after prior")
      
      log.prior[i] <- log(alpha)
      
      #print("after prior2")
      #print(log.prior[i])
      #print(log.prior)
      #rapply( log.prior, f=function(x) ifelse(is.nan(x),-100.00,x), how="replace" )
      #log.prior[is.nan(log.prior)] <- -100.00
      
      log.prior <- log.prior - log.sum(log.prior)#equivalent to num/sum_all_possible_num
      #print("after prior3")
      cand.links <- which(log.prior > log.prior.thresh)
      #print("after cand.links")

      ### compute the likelihood of data point i (and its connectors)
      ### with all other tables (!!! do we need to use "idx"?)

      cand.clusts <- unique(st$cluster[cand.links])#candidate clusters maybe?

      new.lhood <- daply(subset(st, cluster %in% cand.clusts), .(cluster),
                         function (df)
                         lhood.fn(dat[unique(c(df$idx,st[conn.i,"idx"])),]))

      if (length(new.lhood)==1) names(new.lhood) <- cand.clusts

      ### set up the old likelihoods

      old.lhood <- lhood[char(cand.clusts)]
      sum.old.lhood <- sum(old.lhood)

      ### compute the conditional distribution
   
      log.prob <-
        log.prior[cand.links] #+
          sapply(cand.links,
                 function (j) {
                   c.j <- char(st$cluster[j])
                   sum.old.lhood - old.lhood[c.j] + new.lhood[c.j] })

      ### sample from the distribution

      prob <- exp(log.prob - log.sum(log.prob))
      if (length(prob)==1)
        st$customer[i] <- cand.links[1]
      else
        st$customer[i] <- sample(cand.links, 1, prob=prob)
      msg(sprintf(" %d %d", i, st$customer[i]))
      print("distance:")
      print(dist.fn(i, st$customer[i]))

      ### update the score with the prior and update the clusters

      iter.score <- iter.score + log.prior[st$customer[i]]
      st$cluster[conn.i] <- st$cluster[st$customer[i]]
      clust.i.idx <- subset(st, cluster == st$cluster[i])$idx
      lhood[char(st$cluster[i])] <- lhood.fn(dat[clust.i.idx,])
    }

    ### update the summary

    iter.score <- iter.score + sum(lhood)
    score[iter] <- iter.score
    if ((score[iter] > map.score) || (iter==1))
    {
      map.score <- score[iter]
      map.state <- st
    }
    summary <- rbind(summary, summary.fn(dat, iter, st, lhood, alpha))
    if (!is.null(dim(cust.traj))) cust.traj[iter,] <- st$customer
    if (!is.null(dim(clust.traj))) clust.traj[iter,] <- st$cluster
  }

  ### return everything

  list(summary=summary, cust.traj=cust.traj, clust.traj=clust.traj, score=score,
       map.score = map.score, map.state = map.state)
}