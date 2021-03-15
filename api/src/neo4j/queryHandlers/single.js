import driver from 'neo4j/driver';

const querySingleResult = async (statement) => {
  const session = driver.session();

  let result;
  let error;

  try {
    const response = await session.run(statement);

    if (response.records.length === 0) {
      throw new Error('404');
    }

    result = response.records[0].get(0);

    if (Object.values(result).flat().length === 0) {
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
