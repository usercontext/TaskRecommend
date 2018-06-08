library('Matrix')
source("ddcrp-inference.R")

seq.dist <- function(i,j)
{
  return(stdist[i,j])
}

doc.lhood <- function(docs, lambda)
{
  if (is.null(dim(docs)))
    return(exch.dirichlet.lhood(docs, lambda))
  else
    return(exch.dirichlet.lhood(colSums(docs), lambda))
}

doc.lhood.fn <- function(lambda) function (dat) doc.lhood(dat, lambda)


heldout.doc.lhood <- function(doc, dists, alpha, eta, post.dir, decay.fn, state)
{
  # for each doc compute the log prior probability of each component
  log.prior <- safelog(decay.fn(dists))
  log.prior[length(log.prior)+1] <- log(alpha)
  log.prior <- log.prior - log.sum(log.prior)
  
  # for each doc compute the probability of the document under each component
  log.like <- apply(post.dir, 1, function (a) dirichlet.lhood(doc, a))
  names(log.like) <- rownames(post.dir)
  log.like <- log.like[char(state$cluster)]
  log.like[length(log.like) + 1] <- exch.dirichlet.lhood(doc, eta)
  
  # return the sum
  sum(log.prior + log.like)
}


compute.posterior.dirichlets <- function(dat, state, eta)
{
  comps <- sort(unique(state$cluster))
  post.dir <- laply(comps, function (k) colsum(dat[state$cluster==k,]) + eta)
  rownames(post.dir) <- comps
  colnames(post.dir) <- colnames(dat)
  post.dir
}

heldout.lhoods <- function(dat.ho, ho.idx, dat.obs, map.state,
                           dist.fn, decay.fn, alpha, lambda)
{
  one.doc <- function (doc, idx)
  {
    msg(sprintf("computing likelihood for doc %d", idx))
    dists <- laply(seq(1, dim(dat.obs)[1]), function (i) dist.fn(idx, i))
    heldout.doc.lhood(doc, dists, alpha, lambda, post.dir, decay.fn, map.state)
  }
  post.dir <- compute.posterior.dirichlets(dat.obs, map.state, lambda)
  stopifnot(dim(dat.ho)[1] == length(ho.idx))
  laply(1:length(ho.idx), function (i) one.doc(dat.ho[i,], ho.idx[i]))
}


##CIKM script
setwd("C:/Users/prasantab/Downloads/ddcrp_subtasks-master/ddcrp_subtasks-master/ddcrp")
docs <- readLines("Bigram_Quora.csv")
corpus <- Corpus(VectorSource(docs))

dt = DocumentTermMatrix(corpus)
#ft = findFreqTerms(dt, 1, 100)

v = as.matrix(dt)

#stdist = as.matrix(stringdistmatrix(docs))
stdist = read.csv("distance_matrix_research.csv",head=F)

res <- ddcrp.gibbs(dat=v, dist.fn=seq.dist, alpha=1,
                   decay.fn=window.decay(1),
                   doc.lhood.fn(0.2), 1, summary.fn = ncomp.summary,clust.traj=TRUE, cust.traj=TRUE)

print (dim(res$map.state))
clusters = res$map.state
length(unique(clusters$cluster))

write.table(clusters, file="cluster_quora_research.txt", row.names=FALSE)


