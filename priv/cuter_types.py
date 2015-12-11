#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
import cuter_global as cglb
import cuter_logger as clg
import cuter_common as cc

class ErlType:
  """
  Representation of Types in JSON form (as retrieved in the logs).
  """
  @classmethod
  def getType(cls, typ):
    return typ["tp"]

  @classmethod
  def setType(cls, typ, tp):
    typ["tp"] = tp

  @classmethod
  def getArgs(cls, typ):
    return typ["a"]

  @classmethod
  def setArgs(cls, typ, args):
    typ["a"] = args

  @classmethod
  def generateAnyType(cls):
    tp = {}
    cls.setType(tp, cc.JSON_ERLTYPE_ANY)
    return tp

  @classmethod
  def generateTupleType(cls):
    tp = {}
    cls.setType(tp, cc.JSON_ERLTYPE_TUPLE)
    return tp

  @classmethod
  def generateListAnyType(cls):
    tp = {}
    cls.setType(tp, cc.JSON_ERLTYPE_LIST)
    cls.setArgs(tp, cls.generateAnyType())
    return tp

  @classmethod
  def generateNTupleType(cls, sz):
    tp = {}
    cls.setNTupleType(tp, sz)
    return tp

  @classmethod
  def generateConsType(cls):
    tp = {}
    cls.setConsType(tp)
    return tp

  @classmethod
  def isAny(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_ANY

  @classmethod
  def isAtom(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_ATOM

  @classmethod
  def isAtomLit(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_ATOMLIT

  @classmethod
  def isFloat(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_FLOAT

  @classmethod
  def isInteger(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_INTEGER

  @classmethod
  def isIntegerLit(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_INTEGERLIT

  @classmethod
  def isList(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_LIST

  @classmethod
  def isNil(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_NIL

  @classmethod
  def isTuple(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_TUPLE

  @classmethod
  def isTupleDet(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_TUPLEDET

  @classmethod
  def isUnion(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_UNION

  @classmethod
  def isRange(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_RANGE

  @classmethod
  def isNonemptyList(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_NONEMPTY_LIST

  @classmethod
  def isBitstring(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_BITSTRING

  @classmethod
  def isCons(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_CONS

  @classmethod
  def isNTuple(cls, typ):
    return cls.getType(typ) == cc.JSON_ERLTYPE_NTUPLE

  @classmethod
  def setNonEmptyListType(cls, typ):
    cls.setType(typ, cc.JSON_ERLTYPE__NONEMPTY_LIST)

  @classmethod
  def setConsType(cls, typ):
    cls.setType(typ, cc.JSON_ERLTYPE_CONS)
    cls.setArgs(typ, None)

  @classmethod
  def setNilType(cls, typ):
    cls.setType(typ, cc.JSON_ERLTYPE_NIL)
    cls.setArgs(typ, None)

  @classmethod
  def setNTupleType(cls, typ, n):
    cls.setType(typ, cc.JSON_ERLTYPE_NTUPLE)
    cls.setArgs(typ, n)

  @classmethod
  def getListTypeFromNonemptyList(cls, typ):
    tp = deepcopy(typ)
    cls.setType(tp, cc.JSON_ERLTYPE_LIST)
    return tp

class Type:
  """
  Representation of Erlang datatypes used for generating type constraints incrementally.
  """
  def __init__(self, typ):
    self.typ = deepcopy(typ)
    self.isFinal = self.isFinalType(typ)
    self.children = None
    if ErlType.isNonemptyList(typ):
      h = Type(deepcopy(ErlType.getArgs(self.typ)))
      t = Type(ErlType.getListTypeFromNonemptyList(self.typ))
      ErlType.setConsType(self.typ)
      self.isFinal = True
      self.children = [h, t]

  def getChildren(self):
    return self.children

  def getType(self):
    return self.typ

  @classmethod
  def generateAny(cls):
    return Type(ErlType.generateAnyType())

  @classmethod
  def listToTuple(cls, tp):
    # FIXME Retain the type of the list.
    return Type(ErlType.generateTupleType())

  @classmethod
  def tupleToList(cls, tp):
    if tp.isFinal:
      return Type(ErlType.generateListAnyType())
    else:
      # preprocess unions
      if ErlType.isUnion(tp.typ):
        isCnd = lambda x: ErlType.isTuple(x) or ErlType.isTupleDet(x)
        candidates = [t for t in ErlType.getArgs(tp.typ) if isCnd(t)]
        if len(candidates) > 0:
          tp.typ = candidates[0]
          if ErlType.isTupleDet(tp.typ):
            sz = len(ErlType.getArgs(tp.typ))
            tp.matchNTuple(sz)
        else:
          # TODO Log inconsistency
          pass
      # actual type elaborations
      if ErlType.isTuple(tp.typ):
        return Type(ErlType.generateListAnyType())
      elif ErlType.isTupleDet(tp.typ):
        children = tp.getChildren()
        t = Type(ErlType.generateListAnyType())
        for child in reversed(children):
          t = cls.makeCons(child, t)
        return t
      else:
        # TODO Log inconsistency (if is not any())
        return Type(ErlType.generateListAnyType())

  def matchCons(self):
    if not self.isFinal:
      # preprocess unions
      if ErlType.isUnion(self.typ):
        isL = lambda x: ErlType.isList(x) or ErlType.isNonemptyList(x)
        candidates = [tp for tp in ErlType.getArgs(self.typ) if isL(tp)]
        if len(candidates) > 0:
          self.typ = candidates[0]
        else:
          # TODO Log inconsistency
          pass
      # actual type elaborations
      if ErlType.isList(self.typ):
        h = Type(deepcopy(ErlType.getArgs(self.typ)))
        t = Type(deepcopy(self.typ))
        ErlType.setConsType(self.typ)
        self.isFinal = True
        self.children = [h, t]
      elif ErlType.isNonemptyList(self.typ):
        h = Type(deepcopy(ErlType.getArgs(self.typ)))
        t = Type(ErlType.getListTypeFromNonemptyList(self.typ))
        ErlType.setConsType(self.typ)
        self.isFinal = True
        self.children = [h, t]
      elif ErlType.isAny(self.typ):
        pass
      else:
        # TODO Log inconsistency
        pass

  def revMatchCons(self):
    if not self.isFinal:
      # preprocess unions
      if ErlType.isUnion(self.typ):
        candidates = [tp for tp in ErlType.getArgs(self.typ) if not ErlType.isNonemptyList(tp)]
        if len(candidates) > 0:
          ErlType.setArgs(self.typ, candidates)
          for tp in ErlType.getArgs(self.typ):
            if ErlType.isList(tp):
              ErlType.setNilType(tp)
      # actual type elaborations
      if ErlType.isList(self.typ):
        ErlType.setNilType(self.typ)
        self.isFinal = True

  def matchNil(self):
    if not self.isFinal:
      # preprocess unions
      if ErlType.isUnion(self.typ):
        isCnd = lambda x: ErlType.isList(x) or ErlType.isNil(x)
        candidates = [tp for tp in ErlType.getArgs(self.typ) if isCnd(tp)]
        if len(candidates) > 0:
          self.typ = candidates[0]
        else:
          # TODO Log inconsistency
          pass
      # actual type elaborations
      if ErlType.isList(self.typ):
        ErlType.setNilType(self.typ)
        self.isFinal = True
      elif ErlType.isNil(self.typ):
        self.isFinal = True
      elif ErlType.isAny(self.typ):
        pass
      else:
        # TODO Log inconsistency
        pass

  def matchNotNil(self):
    if not self.isFinal:
      # preprocess unions
      if ErlType.isUnion(self.typ):
        candidates = [tp for tp in ErlType.getArgs(self.typ) if not ErlType.isNil(tp)]
        for cnd in candidates:
          if ErlType.isList(cnd):
            ErlType.setNonEmptyListType(cmd)
        if len(candidates) > 0:
          ErlType.setArgs(self.typ, candidates)
        else:
          # TODO Log inconsistency
          pass
      elif ErlType.isList(self.typ):
        self.matchCons()

  def matchNotList(self):
    if not self.isFinal:
      # preprocess unions
      if ErlType.isUnion(self.typ):
        isCnd = lambda x: not ErlType.isList(x) and not ErlType.isNil(x) and not ErlType.isNonemptyList(x)
        candidates = [tp for tp in ErlType.getArgs(self.typ) if isCnd(tp)]
        if len(candidates) > 0:
          ErlType.setArgs(self.typ, candidates)
        else:
          # TODO Log inconsistency
          pass
      if ErlType.isList(self.typ) or ErlType.isNil(self.typ) or ErlType.isNonemptyList(self.typ):
        # TODO Log inconsistency
        pass

  def matchNTuple(self, sz):
    if not self.isFinal:
      # preprocess unions
      if ErlType.isUnion(self.typ):
        isCnd = lambda x: ErlType.isTuple(x) or (ErlType.isTupleDet(x) and len(ErlType.getArgs(x)) == sz)
        candidates = [tp for tp in ErlType.getArgs(self.typ) if isCnd(tp)]
        if len(candidates) > 0:
          self.typ = candidates[0]
        else:
          # TODO Log inconsistency
          pass
      # actual type elaborations
      if ErlType.isTuple(self.typ):
        pass
      elif ErlType.isTupleDet(self.typ) and len(ErlType.getArgs(self.typ)) == sz:
        self.isFinal = True
        self.children = [Type(deepcopy(tp)) for tp in ErlType.getArgs(self.typ)]
        ErlType.setNTupleType(self.typ, sz)
      elif ErlType.isAny(self.typ):
        pass
      else:
        # TODO Log inconsistency
        pass

  def notMatchNTuple(self, sz):
    if not self.isFinal:
      # preprocess unions
      if ErlType.isUnion(self.typ):
        isCnd = lambda x: not (ErlType.isTupleDet(x) and len(ErlType.getArgs(x)) == sz)
        candidates = [tp for tp in ErlType.getArgs(self.typ) if isCnd(tp)]
        if len(candidates) > 0:
          ErlType.setArgs(self.typ, candidates)
        else:
          # TODO Log inconsistency
          pass
      # actual type elaborations
      if ErlType.isTupleDet(self.typ) and len(ErlType.getArgs(self.typ)) == sz:
        # TODO Log inconsistency
        pass

  def notMatchTuple(self):
    if not self.isFinal:
      # preprocess unions
      if ErlType.isUnion(self.typ):
        isCnd = lambda x: not ErlType.isTupleDet(x) and not ErlType.isTuple(x)
        candidates = [tp for tp in ErlType.getArgs(self.typ) if isCnd(tp)]
        if len(candidates) > 0:
          ErlType.setArgs(self.typ, candidates)
        else:
          # TODO Log inconsistency
          pass
      # actual type elaborations
      if ErlType.isTupleDet(self.typ) or ErlType.isTuple(self.typ):
        # TODO Log inconsistency
        pass

  def matchNList(self, sz):
    if sz == 0:
      self.matchNil()
      return []
    else:
      if not self.isFinal:
        self.matchCons()
        if self.children == None:
          return None
      if ErlType.isCons(self.typ):
        h, t = self.children[0], self.children[1]
        rec = t.matchNlist(sz - 1)
        return None if rec == None else [h] + rec
      else:
        return None

  @classmethod
  def makeNTuple(cls, sz, children):
    tp = Type(ErlType.generateNTupleType(sz))
    tp.children = children
    return tp

  @classmethod
  def makeCons(cls, h, t):
    tp = Type(ErlType.generateConsType())
    tp.children = [h, t]
    return tp

  def isFinalType(self, typ):
    if ErlType.isAny(typ):
      return True
    elif ErlType.isAtom(typ):
      return True
    elif ErlType.isAtomLit(typ):
      return True
    elif ErlType.isFloat(typ):
      return True
    elif ErlType.isInteger(typ):
      return True
    elif ErlType.isIntegerLit(typ):
      return True
    elif ErlType.isList(typ):
      return False
    elif ErlType.isNil(typ):
      return True
    elif ErlType.isTuple(typ):
      return True
    elif ErlType.isTupleDet(typ):
      return all(self.isFinalType(t) for t in ErlType.getArgs(typ))
    elif ErlType.isUnion(typ):
      return all(self.isFinalType(t) for t in ErlType.getArgs(typ))
    elif ErlType.isRange(typ):
      return True
    elif ErlType.isNonemptyList(typ):
      return False
    elif ErlType.isBitstring(typ):
      return True
    elif ErlType.isCons(typ):
      return True
    elif ErlType.isNTuple(typ):
      return True

  def isAny(self):
    return ErlType.isAny(self.typ)

  def isAtom(self):
    return ErlType.isAtom(self.typ)

  def isAtomLit(self):
    return ErlType.isAtomLit(self.typ)

  def isFloat(self):
    return ErlType.isFloat(self.typ)

  def isInteger(self):
    return ErlType.isInteger(self.typ)

  def isIntegerLit(self):
    return ErlType.isIntegerLit(self.typ)

  def isList(self):
    return ErlType.isList(self.typ)

  def isNil(self):
    return ErlType.isNil(self.typ)

  def isTuple(self):
    return ErlType.isTuple(self.typ)

  def isTupleDet(self):
    return ErlType.isTupleDet(self.typ)

  def isUnion(self):
    return ErlType.isUnion(self.typ)

  def isRange(self):
    return ErlType.isRange(self.typ)

  def isNonemptyList(self):
    return ErlType.isNonemptyList(self.typ)

  def isBitstring(self):
    return ErlType.isBitstring(self.typ)

  def isCons(self):
    return ErlType.isCons(self.typ)

  def isNTuple(self):
    return ErlType.isNTuple(self.typ)