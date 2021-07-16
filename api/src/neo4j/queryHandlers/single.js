import driver from 'neo4j/driver';

const querySingleResult = async (statement, throwEmptyResponse = true) => {
  const session = driver.session();

  let result;
  let error;

  try {
    const response = await session.readTransaction(t => t.run(statement));
    
    if (throwEmptyResponse && response.records.length === 0) {
      throw new Error('404');
    }

    result = response.records[0].get(0);

    if (throwEmptyResponse && Object.values(result).flat().filter(x => x !== 0).length === 0) {
      // the result contains only empty lists of 0 values
      throw new Error('404');
    }
  } catch (e) {
    error = e;
  } finally {
    await session.close();
  }

  if (error) {
    throw error;
  }

  return result;
};

export default querySingleResult;
